

from app.mcp.models import MCPTransport

from .http import HTTPTransport
from .stdio import STDIOTransport
from .websocket import WebSocketTransport


class TransportManager:

    def create(

        self,

        transport: MCPTransport,

        endpoint: str,

    ):

        if transport == MCPTransport.HTTP:

            return HTTPTransport(endpoint)

        if transport == MCPTransport.WEBSOCKET:

            return WebSocketTransport(endpoint)

        if transport == MCPTransport.STDIO:

            return STDIOTransport(
                endpoint.split()
            )

        raise ValueError(
            f"Unsupported transport: {transport}"
        )