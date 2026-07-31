class SandboxExecutor:

    def __init__(

        self,

        manager,

    ):

        self.manager = manager

    async def run(

        self,

        command,

    ):

        return await self.manager.container_manager.execute(
            command
        )

class SandboxExecution:

    def __init__(

        self,

        runtime,

        monitor,

    ):

        self.runtime = runtime

        self.monitor = monitor

    async def execute(

        self,

        context,

    ):

        ...