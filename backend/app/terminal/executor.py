"""
Safe Terminal Executor.
"""

from __future__ import annotations

import asyncio

from app.terminal.models import (
    CommandResult,
    CommandStatus,
    TerminalCommand,
)


class TerminalExecutor:

    """
    Executes approved commands inside a sandbox.
    """

    async def execute(
        self,
        cmd: TerminalCommand,
    ) -> CommandResult:

        process = await asyncio.create_subprocess_shell(

            cmd.command,

            cwd=cmd.working_directory,

            stdout=asyncio.subprocess.PIPE,

            stderr=asyncio.subprocess.PIPE,

        )

        stdout, stderr = await process.communicate()

        return CommandResult(

            command=cmd.command,

            exit_code=process.returncode,

            stdout=stdout.decode(),

            stderr=stderr.decode(),

            status=(
                CommandStatus.SUCCESS
                if process.returncode == 0
                else CommandStatus.FAILED
            ),
        )