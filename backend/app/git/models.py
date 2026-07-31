from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class GitOperation(str, Enum):

    STATUS = "status"

    ADD = "add"

    COMMIT = "commit"

    DIFF = "diff"

    BRANCH = "branch"


class GitResult(BaseModel):

    success: bool

    operation: GitOperation

    output: str

    commit_hash: str | None = None