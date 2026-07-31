from app.tools.base import ToolResult

from .base import BaseMCPAdapter


class MCPPromptAdapter(BaseMCPAdapter):

    def __init__(

        self,

        client,

        server_id,

        prompt_name,

    ):

        self.client = client

        self.server_id = server_id

        self.prompt_name = prompt_name

    async def execute(

        self,

        **kwargs,

    ):

        response = await self.client.get_prompt(

            self.server_id,

            self.prompt_name,

            kwargs,

        )

        return ToolResult(

            success=response.success,

            data=response.result,

            error=response.error,

        )