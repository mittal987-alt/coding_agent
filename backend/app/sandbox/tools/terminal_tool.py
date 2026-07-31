from __future__ import annotations

import logging
from typing import Any

from app.sandbox.context import ExecutionContext
from app.sandbox.manager import SandboxManager
from app.tools.base import BaseTool
from app.sandbox.factory import SandboxFactory

logger = logging.getLogger(__name__)


class TerminalTool(BaseTool):
    """
    Executes terminal commands inside the secure sandbox.

    Flow:

    Agent
        ↓
    TerminalTool
        ↓
    SandboxManager
        ↓
    Docker Runtime
    """

    name = "terminal"

    description = "Execute shell commands inside an isolated sandbox."

    def __init__(
        self,
        sandbox: SandboxManager,
        factory: SandboxFactory,
    ) -> None:
        self.sandbox = sandbox
        self.factory = factory

    async def execute(
        self,
        *,
        command: str,
        workspace: str,
        language: str = "python",
        environment: dict[str, str] | None = None,
        timeout: int = 300,
        network_enabled: bool = False,
        interactive: bool = False,
    ) -> dict[str, Any]:
        """
        Execute a command inside the sandbox.
        """

        logger.info(
            "Executing command '%s' in workspace '%s'",
            command,
            workspace,
        )

        image = self.factory.image(language)

        context = ExecutionContext(
            workspace=workspace,
            image=image,
            command=command,
            environment=environment or {},
            network_enabled=network_enabled,
            interactive=interactive,
        )

        result = await self.sandbox.run(context)

        return {
            "success": result.success,
            "exit_code": result.exit_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "duration": result.duration,
            "artifacts": result.artifacts,
            "metrics": result.metrics,
        }