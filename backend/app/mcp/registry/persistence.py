import json

from pathlib import Path


class RegistryPersistence:

    def __init__(

        self,

        path="mcp_servers.json",

    ):

        self.path = Path(path)

    def save(

        self,

        servers,

    ):

        self.path.write_text(

            json.dumps(

                [

                    s.model_dump()

                    for s in servers

                ],

                indent=2,

            )

        )

    def load(self):

        if not self.path.exists():

            return []

        return json.loads(

            self.path.read_text()

        )