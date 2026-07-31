from __future__ import annotations

from langgraph.graph import StateGraph

from app.graph.state import AgentState

from app.graph.nodes import *

from app.graph.edges import register_edges

from app.agents.planner import PlannerAgent
from app.agents.repository import RepositoryAgent
from app.agents.retrival import RetrieverAgent
from app.agents.coder import CoderAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.terminal import TerminalAgent
from app.agents.tester import TesterAgent
from app.agents.git import GitAgent
from app.agents.memory import MemoryAgent
from app.agents.responder import ResponderAgent
from app.agents.supervisor import SupervisorAgent


class AIWorkflow:

    def __init__(

        self,

        llm,

        repository,

        retriever,

        memory_manager,

    ):

        self.llm = llm

        self.graph = None

        self.builder = StateGraph(

            AgentState

        )


        self.supervisor = SupervisorAgent(llm)

        self.planner = PlannerAgent(llm)

        self.repository = RepositoryAgent(

            llm,

            repository,

        )

        self.retriever = RetrieverAgent(

            llm,

            retriever,

        )

        self.coder = CoderAgent(llm)

        self.reviewer = ReviewerAgent(llm)

        self.terminal = TerminalAgent(llm)

        self.tester = TesterAgent(llm)

        self.git = GitAgent(llm)

        self.memory = MemoryAgent(

            llm,

            memory_manager,

        )

        self.responder = ResponderAgent(llm)

        self.builder.add_node(

            "supervisor",

            lambda state: supervisor_node(

                state,

                self.supervisor,

            ),

        )

        self.builder.add_node(

            "planner",

            lambda state: planner_node(

                state,

                self.planner,

            ),

        )

        self.builder.add_node(

            "repository",

            lambda state: repository_node(

                state,

                self.repository,

            ),

        )

        self.builder.add_node(

            "retriever",

            lambda state: retriever_node(

                state,

                self.retriever,

            ),

        )

        self.builder.add_node(

            "coder",

            lambda state: coder_node(

                state,

                self.coder,

            ),

        )

        self.builder.add_node(

            "reviewer",

            lambda state: reviewer_node(

                state,

                self.reviewer,

            ),

        )

        self.builder.add_node(

            "terminal",

            lambda state: terminal_node(

                state,

                self.terminal,

            ),

        )

        self.builder.add_node(

            "tester",

            lambda state: tester_node(

                state,

                self.tester,

            ),

        )

        self.builder.add_node(

            "git",

            lambda state: git_node(

                state,

                self.git,

            ),

        )

        self.builder.add_node(

            "memory",

            lambda state: memory_node(

                state,

                self.memory,

            ),

        )

        self.builder.add_node(

            "responder",

            lambda state: responder_node(

                state,

                self.responder,

            ),

        )

        register_edges(

            self.builder

        )

        self.graph = self.builder.compile()

        class AIWorkflow:

    def __init__(...):

        ...

        self.register_nodes()

        register_edges(

            self.builder

        )

        self.graph = self.builder.compile()



            async def run(

        self,

        user_request: str,

        workspace_id: str,

    ):

        state = AgentState(

            user_request=user_request,

            workspace_id=workspace_id,

        )

        result = await self.graph.ainvoke(

            state

        )

        return result



        workflow = AIWorkflow(

    llm,

    repository,

    retriever,

    memory_manager,

)

result = await workflow.run(

    user_request="Implement JWT authentication",

    workspace_id="workspace_1",

)

print(

    result.response

)


