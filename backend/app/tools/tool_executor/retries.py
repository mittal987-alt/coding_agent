import asyncio


class RetryPolicy:

    async def execute(

        self,

        operation,

        retries=3,

    ):

        for attempt in range(retries):

            try:

                return await operation()

            except Exception:

                if attempt == retries - 1:

                    raise

                await asyncio.sleep(

                    2 ** attempt

                )