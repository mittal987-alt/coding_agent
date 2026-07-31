class MCPAdapterRegistry:

    def __init__(self):

        self.adapters = {}

    def register(

        self,

        name,

        adapter,

    ):

        self.adapters[name] = adapter

    def get(

        self,

        name,

    ):

        return self.adapters.get(name)

    def list(self):

        return list(

            self.adapters.values()

        )