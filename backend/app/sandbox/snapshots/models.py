from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class SnapshotStatus(str, Enum):

    CREATED = "created"

    RESTORED = "restored"

    DELETED = "deleted"


class WorkspaceSnapshot(BaseModel):

    id: str

    workspace: str

    execution_id: str

    created_at: datetime

    size_bytes: int

    checksum: str

    status: SnapshotStatus