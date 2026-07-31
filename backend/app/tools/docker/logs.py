class DockerLogs:

    def stream(

        self,

        container,

    ):

        for line in container.logs(

            stream=True,

            follow=True,

        ):

            yield line.decode()