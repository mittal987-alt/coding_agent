class CapabilityCache:

    def __init__(self):

        self.cache = {}

    def put(

        self,

        server,

        capabilities,

    ):

        self.cache[server] = capabilities

    def get(

        self,

        server,

    ):

        return self.cache.get(server)

    def clear(self):

        self.cache.clear()