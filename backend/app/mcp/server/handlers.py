class ToolHandler:

    def __init__(

        self,

        tool_executor,

    ):

        self.tool_executor = tool_executor

    async def call(

        self,

        request,

    ):

        params = request.params

        return await self.tool_executor.execute(

            params["name"],

            **params.get(

                "arguments",

                {},

            ),

        )