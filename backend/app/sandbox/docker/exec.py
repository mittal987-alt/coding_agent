# Exec module
class ExecManager:

    def __init__(

        self,

        container,

    ):

        self.container = container

    def run(

        self,

        command,

    ):

        return self.container.exec_run(

            command,

            stdout=True,

            stderr=True,

        )