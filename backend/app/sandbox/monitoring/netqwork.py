class NetworkMonitor:

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

            "network_rx_bytes": 0,

            "network_tx_bytes": 0,

        }