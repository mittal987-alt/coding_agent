from app.mcp.models import MCPRequest

from .models import Capability


class CapabilityDiscovery:

    async def discover(

        self,

        transport,

        server,

    ):

        capabilities = []

        for method, kind in [

            ("tools/list", "tool"),

            ("resources/list", "resource"),

            ("prompts/list", "prompt"),

        ]:

            response = await transport.send(

                MCPRequest(

                    method=method,

                )

            )

            if response.result:

                for item in response.result.get(

                    kind + "s",

                    [],

                ):

                    capabilities.append(

                        Capability(

                            server=server,

                            name=item["name"],

                            description=item.get(

                                "description",

                                "",

                            ),

                            capability_type=kind,

                            version="1.0",

                        )

                    )

        return capabilities