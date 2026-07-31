class CleanupManager:

    def __init__(

        self,

        handlers,

    ):

        self.handlers = handlers

    async def cleanup(

        self,

        execution_id,

    ):

        results = []

        for handler in self.handlers:

            results.append(

                await handler.cleanup(

                    execution_id

                )

            )

        return results