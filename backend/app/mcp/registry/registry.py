from .models import RegisteredServer


class MCPRegistry:

    def __init__(self):

        self.servers = {}

    def register(

        self,

        server: RegisteredServer,

    ):

        self.servers[server.id] = server

    def unregister(

        self,

        server_id: str,

    ):

        self.servers.pop(server_id, None)

    def get(

        self,

        server_id: str,

    ):

        return self.servers.get(server_id)

    def list(self):

        return list(self.servers.values())