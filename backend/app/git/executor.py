from __future__ import annotations

from app.terminal.executor import TerminalExecutor
from app.terminal.models import TerminalCommand


class GitExecutor:

    def __init__(self):

        self.executor = TerminalExecutor()

    async def status(self):

        return await self.executor.execute(

            TerminalCommand(command="git status --short")

        )

    async def diff(self):

        return await self.executor.execute(

            TerminalCommand(command="git diff")

        )

    async def add(self):

        return await self.executor.execute(

            TerminalCommand(command="git add .")

        )

    async def commit(
        self,
        message: str,
    ):

        return await self.executor.execute(

            TerminalCommand(

                command=f'git commit -m "{message}"'

            )

        )