from app.mcp.models import MCPRequest

from app.mcp.transport.manager import TransportManager

from .cache import CapabilityCache

from .discovery import DiscoveryService

from .session import MCPSession


class MCPClient:

    def __init__(self):

        self.transport_manager = TransportManager()

        self.discovery = DiscoveryService()

        self.cache = CapabilityCache()

        self.sessions = {}

    async def connect(

        self,

        server,

    ):

        transport = self.transport_manager.create(

            server.transport,

            server.endpoint,

        )

        await transport.connect()

        session = MCPSession(

            server=server,

        )

        response = await self.discovery.initialize(

            transport,

        )

        session.initialized = response.success

        self.sessions[server.id] = (

            session,

            transport,

        )

        return session

    
    async def discover_tools(

        self,

        server_id,

     ):

        session, transport = self.sessions[
            server_id
        ]

        response = await self.discovery.list_tools(
            transport
        )

        self.cache.set_tools(

            server_id,

            response.result["tools"],

        )

        return response.result["tools"]

        async def call_tool(

    self,

    server_id,

    tool,

    arguments,

):

    session, transport = self.sessions[
        server_id
    ]

    return await transport.send(

        MCPRequest(

            method="tools/call",

            params={

                "name": tool,

                "arguments": arguments,

            },

        )

    )