class MCPRouter:

    def __init__(self):

        self.routes = {}

    def register(

        self,

        method,

        handler,

    ):

        self.routes[method] = handler

    async def dispatch(

        self,

        request,

    ):

        handler = self.routes.get(

            request.method

        )

        if handler is None:

            raise ValueError(

                f"Unknown method: {request.method}"

            )

        return await handler(request)