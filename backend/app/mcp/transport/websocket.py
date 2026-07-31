import json

import websockets

from app.mcp.models import (
    MCPRequest,
    MCPResponse,
)

from .base import BaseTransport


class WebSocketTransport(BaseTransport):

    def __init__(

        self,

        url: str,

    ):

        self.url = url

        self.connection = None

    async def connect(self):

        self.connection = await websockets.connect(
            self.url
        )

    async def disconnect(self):

        if self.connection:

            await self.connection.close()

    async def send(

        self,

        request: MCPRequest,

    ):

        await self.connection.send(

            request.model_dump_json()

        )

        message = await self.connection.recv()

        return MCPResponse.model_validate(
            json.loads(message)
        )