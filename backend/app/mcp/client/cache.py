class CapabilityCache:

    def __init__(self):

        self.tools = {}

        self.resources = {}

        self.prompts = {}

    def set_tools(

        self,

        server,

        tools,

    ):

        self.tools[server] = tools

    def get_tools(

        self,

        server,

    ):

        return self.tools.get(server)