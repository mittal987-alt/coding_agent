#
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.api.schemas.common import (
    BaseSchema,
    TimestampSchema,
)
class WorkspaceCreateRequest(BaseSchema):
    """
    Create a new workspace.
    """

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    description: str | None = None

    template: str | None = None

    initialize_git: bool = True
class WorkspaceResponse(TimestampSchema):

    id: str

    name: str

    description: str | None = None

    path: str

    git_initialized: bool

    status: Literal[
        "creating",
        "ready",
        "busy",
        "archived",
        "deleted",
    ]

class CloneRepositoryRequest(BaseSchema):

    repository_url: str

    branch: str = "main"

    shallow: bool = False

    depth: int = Field(
        default=1,
        ge=1,
    )
class FileMetadata(BaseSchema):

    path: str

    size: int

    is_directory: bool

    modified_at: datetime

    mime_type: str | None = None
class ReadFileRequest(BaseSchema):

    path: str
class ReadFileResponse(BaseSchema):

    path: str

    content: str

    encoding: str = "utf-8"
class WriteFileRequest(BaseSchema):

    path: str

    content: str

    overwrite: bool = True
class DeleteFileRequest(BaseSchema):

    path: str

    recursive: bool = False
class RenameFileRequest(BaseSchema):

    source: str

    destination: str
class DirectoryListing(BaseSchema):

    path: str

    files: list[FileMetadata]

class TerminalRequest(BaseSchema):

    command: str

    working_directory: str | None = None

    timeout: int = Field(
        default=300,
        ge=1,
        le=3600,
    )
class TerminalResponse(BaseSchema):

    stdout: str

    stderr: str

    exit_code: int

    execution_time_ms: float
class GitStatus(BaseSchema):

    branch: str

    clean: bool

    modified: list[str] = Field(
        default_factory=list,
    )

    added: list[str] = Field(
        default_factory=list,
    )

    deleted: list[str] = Field(
        default_factory=list,
    )

    untracked: list[str] = Field(
        default_factory=list,
    )
class GitCommitRequest(BaseSchema):

    message: str = Field(
        min_length=1,
        max_length=500,
    )
class GitPushRequest(BaseSchema):

    remote: str = "origin"

    branch: str = "main"
class GitPullRequest(BaseSchema):

    remote: str = "origin"

    branch: str = "main"
class WorkspaceStats(BaseSchema):

    total_files: int

    total_directories: int

    total_size_bytes: int

    language_breakdown: dict[str, int] = Field(
        default_factory=dict,
    )

class WorkspaceEvent(BaseSchema):

    event: Literal[
        "created",
        "updated",
        "deleted",
        "file_changed",
        "terminal_output",
        "git_updated",
    ]

    workspace_id: str

    data: dict = Field(
        default_factory=dict,
    )