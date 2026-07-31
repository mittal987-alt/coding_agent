class MCPServer:

    def __init__(

        self,

        router,

        protocol,

        lifecycle,

    ):

        self.router = router

        self.protocol = protocol

        self.lifecycle = lifecycle

    async def handle(

        self,

        payload,

    ):

        request = await self.protocol.parse(

            payload

        )

        result = await self.router.dispatch(

            request

        )

        return await self.protocol.build(

            result

        )