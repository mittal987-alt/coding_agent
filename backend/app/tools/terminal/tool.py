from app.tools.base import (
    BaseTool,
    ToolResult,
)

from .validator import CommandValidator
from .executor import TerminalExecutor
from .models import CommandRequest


class TerminalTool(BaseTool):

    name = "terminal"

    description = "Execute terminal commands safely."

    def __init__(self):

        self.validator = CommandValidator()

        self.executor = TerminalExecutor()

    async def execute(

        self,

        **kwargs,

    ) -> ToolResult:

        request = CommandRequest(**kwargs)

        self.validator.validate(

            request.command

        )

        result = await self.executor.execute(

            request

        )

        return ToolResult(

            success=result.status == "success",

            output=result.stdout,

            metadata=result.model_dump(),

        )