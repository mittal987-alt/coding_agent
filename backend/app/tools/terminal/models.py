 from __future__ import annotations

from enum import Enum
from pydantic import BaseModel


class CommandStatus(str, Enum):

    SUCCESS = "success"

    FAILED = "failed"

    TIMEOUT = "timeout"

    CANCELLED = "cancelled"

    BLOCKED = "blocked"


class CommandRequest(BaseModel):

    command: str

    working_directory: str | None = None

    timeout: int = 300

    environment: dict[str, str] = {}


class CommandResult(BaseModel):

    status: CommandStatus

    exit_code: int | None = None

    stdout: str = ""

    stderr: str = ""

    duration: float = 0.0