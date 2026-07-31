from app.mcp.models import MCPRequest, MCPResponse


class MCPProtocol:

    async def parse(

        self,

        payload: dict,

    ) -> MCPRequest:

        return MCPRequest.model_validate(payload)

    async def build(

        self,

        result,

    ) -> MCPResponse:

        return MCPResponse(

            success=True,

            result=result,

        )