"""
Retriever Agent

Uses the Hybrid Retrieval Engine
to prepare repository context.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.graph.state import AgentState
from app.retrieval.hybrid_retriever import HybridRetriever


class RetrieverAgent(BaseAgent):

    def __init__(
        self,
        llm,
        retriever: HybridRetriever,
    ):

        super().__init__(
            llm=llm,
            name="Retriever",
        )

        self.retriever = retriever

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        query = self.build_query(state)

        prompt = self.retriever.retrieve(query)

        state.retrieval_prompt = prompt

        return state

    def build_query(
        self,
        state: AgentState,
    ) -> str:

        parts = [

            f"User Request:\n{state.user_request}",

            f"Plan:\n{state.plan}",

        ]

        if state.tasks:

            parts.append(

                "Tasks:\n"

                + "\n".join(

                    f"- {task}"

                    for task in state.tasks

                )

            )

        return "\n\n".join(parts)