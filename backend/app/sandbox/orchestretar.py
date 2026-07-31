class SandboxOrchestrator:

    def __init__(

        self,

        manager,

    ):

        self.manager = manager

    async def run_tests(

        self,

        workspace,

    ):

        ...

    async def build(

        self,

        workspace,

    ):

        ...

    async def lint(

        self,

        workspace,

    ):

        ...

    async def benchmark(

        self,

        workspace,

    ):

        ...