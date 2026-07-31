class OutputStreamer:

    async def stream(

        self,

        process,

        callback,

    ):

        while True:

            line = await process.stdout.readline()

            if not line:

                break

            await callback(

                line.decode()

            )