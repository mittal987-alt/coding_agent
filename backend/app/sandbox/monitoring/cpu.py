class CPUMonitor:

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

            "cpu_percent": self.calculate(

                stats

            )

        }

    def calculate(

        self,

        stats,

    ):

        # Docker CPU calculation

        return 0.0