class MonitoringManager:

    def __init__(

        self,

        collectors,

    ):

        self.collectors = collectors

    async def collect(self):

        metrics = {}

        for collector in self.collectors:

            metrics.update(

                await collector.collect()

            )

        return metrics

        class MonitoringManager:

    def __init__(

        self,

        collectors,

    ):

        self.collectors = collectors

    async def collect(self):

        metrics = {}

        for collector in self.collectors:

            metrics.update(

                await collector.collect()

            )

        return metrics