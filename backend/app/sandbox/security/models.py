from enum import Enum
from pydantic import BaseModel


class SecurityDecision(str, Enum):

    ALLOW = "allow"

    DENY = "deny"

    REQUIRE_APPROVAL = "require_approval"


class ExecutionRequest(BaseModel):

    command: str

    working_directory: str

    environment: dict[str, str]

    timeout: int


class SecurityResult(BaseModel):

    decision: SecurityDecision

    reason: str | None = None