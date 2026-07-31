import asyncio


class CapabilityWatcher:

    def __init__(

        self,

        registry,

        discovery,

    ):

        self.registry = registry

        self.discovery = discovery

    async def watch(

        self,

        interval=300,

    ):

        while True:

            # Refresh capabilities
            # Detect additions/removals
            # Update registry

            await asyncio.sleep(

                interval

            )