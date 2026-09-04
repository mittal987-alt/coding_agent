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

        raw_text = response.strip()
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            raw_text = "\n".join(lines).strip()

        try:
            plan = json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                plan = json.loads(raw_text[start : end + 1])
            else:
                plan = {"summary": raw_text, "tasks": [], "files": []}

        state.plan = plan.get("summary", "")

        state.tasks = plan.get("tasks", [])

        state.modified_files = plan.get("files", [])

        return state