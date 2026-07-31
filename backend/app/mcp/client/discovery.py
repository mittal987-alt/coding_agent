from app.mcp.models import MCPRequest


class DiscoveryService:

    async def initialize(

        self,

        transport,

    ):

        return await transport.send(

            MCPRequest(

                method="initialize",

            )

        )

    async def list_tools(

        self,

        transport,

    ):

        return await transport.send(

            MCPRequest(

                method="tools/list",

            )

        )

    async def list_resources(

        self,

        transport,

    ):

        return await transport.send(

            MCPRequest(

                method="resources/list",

            )

        )

    async def list_prompts(

        self,

        transport,

    ):

        return await transport.send(

            MCPRequest(

                method="prompts/list",

            )

        )