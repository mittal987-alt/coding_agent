from app.tools.base import (
    BaseTool,
    ToolResult,
)

from .manager import DockerManager
from .executor import DockerExecutor
from .models import DockerRequest


class DockerTool(BaseTool):

    name = "docker"

    description = "Execute commands inside Docker."

    def __init__(self):

        self.manager = DockerManager()

        self.executor = DockerExecutor()

    async def execute(

        self,

        **kwargs,

    ):

        request = DockerRequest(

            **kwargs

        )

        container = self.manager.create(

            request.image,

            request.workspace,

        )

        code, output = self.executor.execute(

            container,

            request.command,

        )

        container.remove(

            force=True,

        )

        return ToolResult(

            success=code == 0,

            output=output,

        )