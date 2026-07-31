class MemoryMonitor:

    def __init__(

        self,

        container,

    ):

        self.container = container

    async def collect(self):

        stats = self.container.stats(

            stream=False

        )

        return {

            "memory_mb":

                stats["memory_stats"]["usage"]

                / (1024 * 1024)

        }