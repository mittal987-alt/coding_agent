from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.prompts.response import (
    RESPONDER_SYSTEM_PROMPT,
)

from app.response.models import FinalResponse


class ResponderAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(

            llm,

            "Responder",

        )

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        prompt = f"""
User Request

{state.user_request}

Plan

{state.plan}

Tasks

{state.tasks}

Files

{state.modified_files}

Review

{state.review}

Tests

{state.test_output}

Commit

{state.git_commit_message}

Hash

{state.commit_hash}
"""

        response = await self.invoke_llm(

            RESPONDER_SYSTEM_PROMPT,

            prompt,

        )

        result = FinalResponse.model_validate_json(
            response
        )

        state.response = result.model_dump_json(
            indent=2
        )

        return state