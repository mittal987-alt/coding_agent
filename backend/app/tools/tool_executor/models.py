from enum import Enum
from typing import Any

from pydantic import BaseModel


class ExecutionStatus(str, Enum):

    SUCCESS = "success"

    FAILED = "failed"

    BLOCKED = "blocked"

    TIMEOUT = "timeout"

    RETRYING = "retrying"


class ToolExecutionRequest(BaseModel):

    tool: str

    parameters: dict[str, Any]

    agent: str


class ToolExecutionResult(BaseModel):

    status: ExecutionStatus

    output: str

    metadata: dict = {}