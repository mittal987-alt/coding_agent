from app.terminal.executor import TerminalExecutor
from app.terminal.models import TerminalCommand


class TestExecutor:

    def __init__(self):

        self.executor = TerminalExecutor()

    async def run_pytest(self):

        return await self.executor.execute(

            TerminalCommand(

                command="pytest"

            )

        )

    async def run_jest(self):

        return await self.executor.execute(

            TerminalCommand(

                command="npm test"

            )

        )

    async def run_flutter(self):

        return await self.executor.execute(

            TerminalCommand(

                command="flutter test"

            )

        )