"""
Workflow Router

Determines the next LangGraph node to execute based on current AgentState.

Routing priority (top = highest):
  1. HITL pending          → __interrupt__ (pauses for human approval)
  2. No plan               → planner
  3. No repository index   → repository
  4. No retrieval context  → retriever
  5. No code edits         → coder
  6. Review not done       → reviewer
  7. Review failed         → coder  (re-generate)
  8. No terminal output    → terminal
  9. No test output        → tester
 10. Tests failed + retries remain  → evaluator
 11. Tests failed + retries exhausted → responder (HITL handled by evaluator)
 12. No git commit         → git
 13. Memory not stored     → memory
 14. No final response     → responder
 15. All done              → END
"""

from __future__ import annotations

import logging

from langgraph.graph import END

from app.graph.state import AgentState

logger = logging.getLogger(__name__)

# Maximum TDD correction iterations before routing to responder
MAX_RETRIES: int = 3


class WorkflowRouter:
    """
    Stateless conditional edge function for the LangGraph StateGraph.

    Called after every node completes to determine the next node.
    """

    def route(self, state: AgentState) -> str:
        """
        Inspect AgentState and return the name of the next node.

        Args:
            state: Current AgentState snapshot.

        Returns:
            Node name string, or END sentinel.
        """

        # ------------------------------------------------------------------
        # 1. Human-in-the-loop: pause if approval is awaited
        # ------------------------------------------------------------------
        if state.hitl_pending and state.hitl_approved is None:
            logger.debug("Router: HITL pending on node=%s", state.hitl_node_id)
            # LangGraph interrupt_before handles the actual pause;
            # returning the blocked node name keeps graph consistent.
            return state.hitl_node_id or END

        # ------------------------------------------------------------------
        # 2. Planning phase
        # ------------------------------------------------------------------
        if not state.plan:
            return "planner"

        # ------------------------------------------------------------------
        # 3. Repository indexing
        # ------------------------------------------------------------------
        if state.repository is None:
            return "repository"

        # ------------------------------------------------------------------
        # 4. RAG retrieval
        # ------------------------------------------------------------------
        if not state.retrieval_prompt:
            return "retriever"

        # ------------------------------------------------------------------
        # 5. Code generation
        # ------------------------------------------------------------------
        if not state.code_edits:
            return "coder"

        # ------------------------------------------------------------------
        # 6. Code review
        # ------------------------------------------------------------------
        if not state.review:
            return "reviewer"

        # ------------------------------------------------------------------
        # 7. Review failed — regenerate
        # ------------------------------------------------------------------
        if not state.review_passed:
            logger.debug("Router: review failed, re-routing to coder")
            return "coder"

        # ------------------------------------------------------------------
        # 8. Terminal execution
        # ------------------------------------------------------------------
        if not state.terminal_output:
            return "terminal"

        # ------------------------------------------------------------------
        # 9. Test execution
        # ------------------------------------------------------------------
        if not state.test_output:
            return "tester"

        # ------------------------------------------------------------------
        # 10 & 11. TDD self-correction via EvaluatorAgent
        # ------------------------------------------------------------------
        if not state.tests_passed:
            if state.retry_count < MAX_RETRIES:
                logger.debug(
                    "Router: tests failed, retry %d/%d → evaluator",
                    state.retry_count,
                    MAX_RETRIES,
                )
                return "evaluator"
            else:
                logger.warning(
                    "Router: max retries (%d) exhausted → responder",
                    MAX_RETRIES,
                )
                return "responder"

        # EvaluatorAgent has set should_retry=True: coder must fix the code
        if state.should_retry:
            logger.debug(
                "Router: evaluator flagged should_retry → coder (retry %d)",
                state.retry_count,
            )
            # Reset test output so tester runs again after coder
            state.test_output = None
            state.tests_passed = False
            return "coder"

        # ------------------------------------------------------------------
        # 12. Git commit
        # ------------------------------------------------------------------
        if not state.commit_hash:
            return "git"

        # ------------------------------------------------------------------
        # 13. Memory persistence
        # ------------------------------------------------------------------
        if state.memory_count == 0:
            return "memory"

        # ------------------------------------------------------------------
        # 14. Final response
        # ------------------------------------------------------------------
        if not state.response:
            return "responder"

        # ------------------------------------------------------------------
        # 15. Done
        # ------------------------------------------------------------------
        return END