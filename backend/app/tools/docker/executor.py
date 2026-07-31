class DockerExecutor:

    def execute(

        self,

        container,

        command,

    ):

        result = container.exec_run(

            command

        )

        return result.exit_code, result.output.decode()