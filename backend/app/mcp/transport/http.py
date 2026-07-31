import httpx

from app.mcp.models import (
    MCPRequest,
    MCPResponse,
)

from .base import BaseTransport


class HTTPTransport(BaseTransport):

    def __init__(

        self,

        endpoint: str,

    ):

        self.endpoint = endpoint

        self.client = httpx.AsyncClient()

    async def connect(self):

        pass

    async def disconnect(self):

        await self.client.aclose()

    async def send(

        self,

        request: MCPRequest,

    ) -> MCPResponse:

        response = await self.client.post(

            self.endpoint,

            json=request.model_dump(),

        )

        return MCPResponse.model_validate(
            response.json()
        )