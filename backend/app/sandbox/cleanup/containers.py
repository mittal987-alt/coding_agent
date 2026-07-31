class ContainerCleanup:

    def __init__(

        self,

        docker_runtime,

    ):

        self.runtime = docker_runtime

    async def cleanup(

        self,

        execution_id,

    ):

        ...