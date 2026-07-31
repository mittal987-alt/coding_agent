from enum import Enum
from datetime import datetime

from pydantic import BaseModel


class ArtifactType(str, Enum):

    LOG = "log"

    REPORT = "report"

    COVERAGE = "coverage"

    BINARY = "binary"

    SCREENSHOT = "screenshot"

    DOCUMENTATION = "documentation"

    PATCH = "patch"

    OTHER = "other"


class Artifact(BaseModel):

    id: str

    execution_id: str

    name: str

    path: str

    artifact_type: ArtifactType

    size_bytes: int

    created_at: datetime

    metadata: dict = {}