from __future__ import annotations

import asyncio
import time

from .models import (
    CommandRequest,
    CommandResult,
    CommandStatus,
)


class TerminalExecutor:

    async def execute(

        self,

        request: CommandRequest,

    ) -> CommandResult:

        start = time.perf_counter()

        try:

            process = await asyncio.create_subprocess_shell(

                request.command,

                cwd=request.working_directory,

                env=request.environment or None,

                stdout=asyncio.subprocess.PIPE,

                stderr=asyncio.subprocess.PIPE,

            )

            stdout, stderr = await asyncio.wait_for(

                process.communicate(),

                timeout=request.timeout,

            )

            status = (

                CommandStatus.SUCCESS

                if process.returncode == 0

                else CommandStatus.FAILED

            )

            return CommandResult(

                status=status,

                exit_code=process.returncode,

                stdout=stdout.decode(),

                stderr=stderr.decode(),

                duration=time.perf_counter() - start,

            )

        except asyncio.TimeoutError:

            process.kill()

            await process.wait()

            return CommandResult(

                status=CommandStatus.TIMEOUT,

                duration=time.perf_counter() - start,

            )