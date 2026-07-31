class ToolRouter:

    def __init__(

        self,

        registry,

    ):

        self.registry = registry

    def find(

        self,

        tool_name,

    ):

        for server in self.registry.list():

            if tool_name in server.tools:

                return server

        return None