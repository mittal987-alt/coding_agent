class ArtifactManager:

    def __init__(

        self,

        collector,

        storage,

        registry,

    ):

        self.collector = collector

        self.storage = storage

        self.registry = registry

    async def collect(

        self,

        workspace,

        execution_id,

    ):

        artifacts = await self.collector.collect(

            workspace,

            execution_id,

        )

        for artifact in artifacts:

            await self.storage.save(

                artifact

            )

            self.registry.register(

                artifact

            )

        return artifacts