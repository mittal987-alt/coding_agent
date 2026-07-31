from __future__ import annotations

import json

from app.agents.base import BaseAgent
from app.graph.state import AgentState

from app.prompts.terminal import (
    TERMINAL_SYSTEM_PROMPT,
)

from app.terminal.executor import TerminalExecutor
from app.terminal.models import TerminalCommand


class TerminalAgent(BaseAgent):

    def __init__(self, llm):

        super().__init__(
            llm,
            "Terminal",
        )

        self.executor = TerminalExecutor()

    async def run(
        self,
        state: AgentState,
    ) -> AgentState:

        prompt = f"""
Plan:

{state.plan}

Modified Files:

{state.modified_files}

Determine the next command to execute.
"""

        response = await self.invoke_llm(

            TERMINAL_SYSTEM_PROMPT,

            prompt,

        )

        command = TerminalCommand.model_validate_json(
            response
        )

        result = await self.executor.execute(
            command
        )

        state.terminal_output = (
            result.stdout
            + "\n"
            + result.stderr
        )

        state.terminal_success = (
            result.status.value == "success"
        )

        state.last_command = result.command

        return state