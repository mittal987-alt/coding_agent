from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class CommandStatus(str, Enum):

    SUCCESS = "success"

    FAILED = "failed"

    BLOCKED = "blocked"

    TIMEOUT = "timeout"


class TerminalCommand(BaseModel):

    command: str

    working_directory: str = "."


class CommandResult(BaseModel):

    command: str

    exit_code: int

    stdout: str

    stderr: str

    status: CommandStatus