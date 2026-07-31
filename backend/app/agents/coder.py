"""
Coder Agent

Generates structured code edits.
"""

from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.prompts.coder import (
    CODER_SYSTEM_PROMPT,
    CODER_USER_TEMPLATE,
)

from app.coding.models import (
    CodingResult,
)


class CoderAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(
            llm=llm,
            name="Coder",
        )

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        prompt = CODER_USER_TEMPLATE.format(

            request=state.user_request,

            plan=state.plan,

            context=state.retrieval_prompt,

        )

        response = await self.invoke_llm(

            CODER_SYSTEM_PROMPT,

            prompt,

        )

        data = json.loads(response)

        result = CodingResult.model_validate(data)

        state.generated_code = result.summary

        state.code_edits = result.edits

        state.modified_files = [

            edit.path

            for edit in result.edits

        ]

        return state