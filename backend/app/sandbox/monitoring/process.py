class ProcessMonitor:

    def __init__(

        self,

        container,

    ):

        self.container = container

    async def collect(self):

        processes = self.container.top()

        return {

            "process_count":

                len(

                    processes["Processes"]

                )

        }