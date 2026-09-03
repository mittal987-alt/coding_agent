"""
AIWorkflow — LangGraph Execution Graph

Assembles all agent nodes into a directed state graph and compiles it
with HITL interrupt guards on high-risk nodes.

Graph shape (happy path):
  supervisor → planner → repository → retriever → coder
      → reviewer → terminal → tester → evaluator
      → (retry? coder) → git → memory → responder → END

HITL interrupt_before nodes: ["git", "terminal"]
EvaluatorAgent TDD loop: tester → evaluator → (coder × N) → git
"""

from __future__ import annotations

import logging

from langgraph.graph import StateGraph

from app.graph.state import AgentState
from app.graph.nodes import (
    supervisor_node,
    planner_node,
    repository_node,
    retriever_node,
    coder_node,
    reviewer_node,
    terminal_node,
    tester_node,
    evaluator_node,
    git_node,
    memory_node,
    responder_node,
)
from app.graph.edges import register_edges

from app.agents.planner import PlannerAgent
from app.agents.repository import RepositoryAgent
from app.agents.retrival import RetrieverAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.terminal import TerminalAgent
from app.agents.tester import TesterAgent
from app.agents.evaluator import EvaluatorAgent
from app.agents.git import GitAgent
from app.agents.memory import MemoryAgent
from app.agents.responder import ResponderAgent
from app.agents.supervisor import SupervisorAgent

logger = logging.getLogger(__name__)

# Nodes that pause for human approval before executing
HITL_INTERRUPT_NODES: list[str] = ["git", "terminal"]


class AIWorkflow:
    """
    Assembles the LangGraph StateGraph for the autonomous coding pipeline.

    Args:
        llm:            Configured LangChain BaseChatModel instance.
        repository:     RepositoryIndex object for the active workspace.
        retriever:      VectorRetriever for the active workspace.
        memory_manager: MemoryManager for episodic conversation memory.
        max_retries:    Maximum TDD self-correction iterations (default: 3).
        enable_hitl:    If True, compile with interrupt_before HITL guards.
    """

    def __init__(
        self,
        llm,
        repository,
        retriever,
        memory_manager,
        max_retries: int = 3,
        enable_hitl: bool = True,
    ) -> None:
        self.llm = llm
        self.enable_hitl = enable_hitl
        self.graph = None

        # ------------------------------------------------------------------
        # Instantiate all agents
        # ------------------------------------------------------------------
        self.supervisor = SupervisorAgent(llm)
        self.planner = PlannerAgent(llm)
        self.repository_agent = RepositoryAgent(llm, repository)
        self.retriever_agent = RetrieverAgent(llm, retriever)
        self.coder = CoderAgent(llm)
        self.reviewer = ReviewerAgent(llm)
        self.terminal = TerminalAgent(llm)
        self.tester = TesterAgent(llm)
        self.evaluator = EvaluatorAgent(llm, max_retries=max_retries)
        self.git = GitAgent(llm)
        self.memory = MemoryAgent(llm, memory_manager)
        self.responder = ResponderAgent(llm)

        # ------------------------------------------------------------------
        # Build state graph
        # ------------------------------------------------------------------
        self.builder = StateGraph(AgentState)
        self._register_nodes()
        register_edges(self.builder)
        self._compile()

        logger.info(
            "AIWorkflow compiled (HITL=%s, max_retries=%d)",
            enable_hitl,
            max_retries,
        )

    # ------------------------------------------------------------------
    # Node registration
    # ------------------------------------------------------------------

    def _register_nodes(self) -> None:
        """Add all agent nodes to the StateGraph builder."""

        self.builder.add_node(
            "supervisor",
            lambda state: supervisor_node(state, self.supervisor),
        )
        self.builder.add_node(
            "planner",
            lambda state: planner_node(state, self.planner),
        )
        self.builder.add_node(
            "repository",
            lambda state: repository_node(state, self.repository_agent),
        )
        self.builder.add_node(
            "retriever",
            lambda state: retriever_node(state, self.retriever_agent),
        )
        self.builder.add_node(
            "coder",
            lambda state: coder_node(state, self.coder),
        )
        self.builder.add_node(
            "reviewer",
            lambda state: reviewer_node(state, self.reviewer),
        )
        self.builder.add_node(
            "terminal",
            lambda state: terminal_node(state, self.terminal),
        )
        self.builder.add_node(
            "tester",
            lambda state: tester_node(state, self.tester),
        )
        self.builder.add_node(
            "evaluator",
            lambda state: evaluator_node(state, self.evaluator),
        )
        self.builder.add_node(
            "git",
            lambda state: git_node(state, self.git),
        )
        self.builder.add_node(
            "memory",
            lambda state: memory_node(state, self.memory),
        )
        self.builder.add_node(
            "responder",
            lambda state: responder_node(state, self.responder),
        )

    # ------------------------------------------------------------------
    # Graph compilation
    # ------------------------------------------------------------------

    def _compile(self) -> None:
        """
        Compile the StateGraph into an executable graph.

        When enable_hitl=True, the graph pauses before HITL_INTERRUPT_NODES
        and waits for human approval via the /api/v1/hitl/approve endpoint.
        """
        compile_kwargs: dict = {}
        if self.enable_hitl:
            compile_kwargs["interrupt_before"] = HITL_INTERRUPT_NODES

        self.graph = self.builder.compile(**compile_kwargs)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run(
        self,
        user_request: str,
        workspace_id: int,
        conversation_id: str | None = None,
    ) -> AgentState:
        """
        Execute the full autonomous coding pipeline for a user request.

        Args:
            user_request:    Developer's natural language coding request.
            workspace_id:    Active workspace / repository ID.
            conversation_id: Optional session ID for memory continuity.

        Returns:
            Final AgentState after the graph completes.
        """
        initial_state = AgentState(
            user_request=user_request,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
        )

        result = await self.graph.ainvoke(initial_state)
        return result

    async def stream(
        self,
        user_request: str,
        workspace_id: int,
        conversation_id: str | None = None,
        workflow_id: str | None = None,
    ):
        """
        Stream AgentState updates as each node completes.

        When workflow_id is provided, also publishes node_started / node_completed
        events to the SSE queue via app.api.v1.stream.publish_event so the
        frontend GraphVisualizer animates in real time.

        Yields:
            (node_name: str, state: AgentState) tuples for each completed node.
        """
        # Import publish_event lazily to avoid circular import
        try:
            from app.api.v1.stream import publish_event, NODE_META
            _stream_enabled = workflow_id is not None
        except ImportError:
            _stream_enabled = False

        initial_state = AgentState(
            user_request=user_request,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
        )

        prev_node: str | None = None

        async for chunk in self.graph.astream(
            initial_state,
            stream_mode="updates",
        ):
            # chunk is a dict: {node_name: updated_state_dict}
            for node_name, state_update in chunk.items():
                # Emit node_started for the newly running node
                if _stream_enabled and node_name != prev_node:
                    meta = NODE_META.get(node_name, {"name": node_name, "role": ""})
                    await publish_event(workflow_id, {
                        "type": "node_started",
                        "node_id": node_name,
                        "node_name": meta["name"],
                        "role": meta["role"],
                    })
                    prev_node = node_name

                yield node_name, state_update

