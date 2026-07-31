from shlex import split

from app.graph.constants import ALLOWED_TERMINAL_COMMANDS


class CommandValidator:

    def validate(

        self,

        command: str,

    ):

        parts = split(command)

        if not parts:

            raise ValueError("Empty command.")

        executable = parts[0]

        if executable not in ALLOWED_TERMINAL_COMMANDS:

            raise PermissionError(

                f"{executable} is not allowed."

            )

        return True