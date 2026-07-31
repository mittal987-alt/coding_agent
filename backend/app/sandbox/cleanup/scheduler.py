import asyncio


class CleanupScheduler:

    async def run(

        self,

        interval=3600,

    ):

        while True:

            # Execute cleanup tasks

            await asyncio.sleep(

                interval

            )