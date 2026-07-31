from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.tools.terminal_tool import TerminalTool

logger = logging.getLogger(__name__)


class TerminalAgent(BaseAgent):
    """
    Agent responsible for executing shell commands.

    Planner
         │
         ▼
    TerminalAgent
         │
         ▼
    TerminalTool
         │
         ▼
    SandboxManager
    """

    name = "terminal_agent"

    description = (
        "Executes shell commands inside an isolated sandbox."
    )

    def __init__(
        self,
        terminal_tool: TerminalTool,
    ) -> None:

        super().__init__()

        self.terminal_tool = terminal_tool

    async def execute_command(
        self,
        *,
        command: str,
        workspace: str,
        language: str = "python",
        environment: dict[str, str] | None = None,
        timeout: int = 300,
        network_enabled: bool = False,
    ) -> dict[str, Any]:
        """
        Execute a terminal command.

        Returns:
            Standardized execution result.
        """

        logger.info(
            "TerminalAgent executing: %s",
            command,
        )

        return await self.terminal_tool.execute(
            command=command,
            workspace=workspace,
            language=language,
            environment=environment,
            timeout=timeout,
            network_enabled=network_enabled,
        )

    async def run(
        self,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        """
        LangGraph entrypoint.
        """

        result = await self.execute_command(
            command=state["command"],
            workspace=state["workspace"],
            language=state.get(
                "language",
                "python",
            ),
            environment=state.get(
                "environment",
                {},
            ),
            timeout=state.get(
                "timeout",
                300,
            ),
            network_enabled=state.get(
                "network_enabled",
                False,
            ),
        )

        state["execution_result"] = result

        return state

    async def health_check(self) -> bool:
        """
        Simple agent health check.
        """
        return True