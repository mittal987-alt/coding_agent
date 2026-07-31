import docker


class DockerManager:

    def __init__(self):

        self.client = docker.from_env()

    def create(

        self,

        image,

        workspace,

    ):

        container = self.client.containers.run(

            image,

            command="sleep infinity",

            volumes={

                workspace: {

                    "bind": "/workspace",

                    "mode": "rw",

                }

            },

            working_dir="/workspace",

            detach=True,

        )

        return container