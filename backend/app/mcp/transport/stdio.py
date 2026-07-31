import asyncio

from app.mcp.models import (
    MCPRequest,
    MCPResponse,
)

from .base import BaseTransport


class STDIOTransport(BaseTransport):

    def __init__(

        self,

        command: list[str],

    ):

        self.command = command

        self.process = None

    async def connect(self):

        self.process = await asyncio.create_subprocess_exec(

            *self.command,

            stdin=asyncio.subprocess.PIPE,

            stdout=asyncio.subprocess.PIPE,

        )

    async def disconnect(self):

        if self.process:

            self.process.kill()

            await self.process.wait()

    async def send(

        self,

        request: MCPRequest,

    ):

        payload = (
            request.model_dump_json() + "\n"
        ).encode()

        self.process.stdin.write(payload)

        await self.process.stdin.drain()

        response = await self.process.stdout.readline()

        return MCPResponse.model_validate_json(
            response
        )