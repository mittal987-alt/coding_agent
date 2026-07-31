from enum import Enum
from pydantic import BaseModel


class CleanupStatus(str, Enum):

    SUCCESS = "success"

    FAILED = "failed"

    PARTIAL = "partial"


class CleanupResult(BaseModel):

    status: CleanupStatus

    resources_removed: int

    errors: list[str] = []