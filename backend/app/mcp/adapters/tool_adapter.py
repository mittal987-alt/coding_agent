from app.tools.base import ToolResult

from .base import BaseMCPAdapter


class MCPToolAdapter(BaseMCPAdapter):

    def __init__(

        self,

        client,

        server_id,

        tool_name,

    ):

        self.client = client

        self.server_id = server_id

        self.tool_name = tool_name

    async def execute(

        self,

        **kwargs,

    ):

        response = await self.client.call_tool(

            self.server_id,

            self.tool_name,

            kwargs,

        )

        return ToolResult(

            success=response.success,

            data=response.result,

            error=response.error,

        )