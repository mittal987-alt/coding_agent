"""
Planner Agent

Creates execution plans for the AI Software Engineer.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.graph.state import AgentState
from app.prompts.planner import (
    PLANNER_SYSTEM_PROMPT,
    PLANNER_USER_TEMPLATE,
)


class PlannerAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(

            llm=llm,

            name="Planner",

        )

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        repository_context = state.retrieval_prompt or ""

        prompt = PLANNER_USER_TEMPLATE.format(

            request=state.user_request,

            repository=repository_context,

        )

        response = await self.invoke_llm(

            PLANNER_SYSTEM_PROMPT,

            prompt,

        )

        plan = json.loads(response)

        state.plan = plan["summary"]

        state.tasks = plan["tasks"]

        state.modified_files = plan["files"]

        return state