class BaseMiddleware:

    async def before(

        self,

        request,

    ):

        return request

    async def after(

        self,

        response,

    ):

        return response