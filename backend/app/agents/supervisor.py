"""
Supervisor Agent

Controls the LangGraph workflow.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.graph.state import AgentState
from app.prompts.supervisor import (
    SUPERVISOR_SYSTEM_PROMPT,
)


class SupervisorAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(

            llm=llm,

            name="Supervisor",

        )

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        summary = f"""
User Request:
{state.user_request}

Current Plan:
{state.plan}

Tasks:
{state.tasks}

Review Passed:
{state.review_passed}

Tests Passed:
{state.tests_passed}

Terminal Success:
{state.terminal_success}

Modified Files:
{state.modified_files}
"""

        response = await self.invoke_llm(

            SUPERVISOR_SYSTEM_PROMPT,

            summary,

        )

        decision = json.loads(response)

        state.next_agent = decision["next_agent"]

        return state