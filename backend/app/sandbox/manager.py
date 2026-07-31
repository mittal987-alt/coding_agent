class MCPServer:

    def __init__(

        self,

        router,

        protocol,

        lifecycle,

    ):

        self.router = router

        self.protocol = protocol

        self.lifecycle = lifecycle

    async def handle(

        self,

        payload,

    ):

        request = await self.protocol.parse(

            payload

        )

        result = await self.router.dispatch(

            request

        )

        return await self.protocol.build(

            result

        )

class SandboxManager:

    def __init__(

        self,

        security,

        runtime,

        execution,

        artifacts,

        cleanup,

    ):

        self.security = security

        self.runtime = runtime

        self.execution = execution

        self.artifacts = artifacts

        self.cleanup = cleanup

    async def run(

        self,

        context,

    ):

        decision = await self.security.validate(
            context
        )

        if decision.decision != "allow":

            raise PermissionError(
                decision.reason
            )

        result = await self.execution.execute(
            context
        )

        result.artifacts = await self.artifacts.collect(
            context.workspace
        )

        await self.cleanup.cleanup(
            context.execution_id
        )

        return result