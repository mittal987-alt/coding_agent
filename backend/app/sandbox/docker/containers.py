# Containers module
class ContainerManager:

    def __init__(

        self,

        client,

    ):

        self.client = client

    def create(

        self,

        image,

        workspace,

        limits,

    ):

        return self.client.containers.run(

            image,

            command="sleep infinity",

            detach=True,

            working_dir="/workspace",

            volumes={

                workspace: {

                    "bind": "/workspace",

                    "mode": "rw",

                }

            },

            mem_limit=f"{limits.memory_mb}m",

            cpu_quota=int(

                limits.cpu * 100000

            ),

            network_mode="none",

            security_opt=[

                "no-new-privileges"

            ],

            cap_drop=["ALL"],

            read_only=True,

        )