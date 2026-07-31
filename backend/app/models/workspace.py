from __future__ import annotations

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    JSON,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

import uuid
from app.models.base import Entity

class Workspace(Entity):
    """
    Local development workspace.
    """

    __tablename__ = "workspaces"

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        String(2048),
        unique=True,
        nullable=False,
    )

    root_directory: Mapped[str | None] = mapped_column(
        String(2048),
    )
    current_branch: Mapped[str] = mapped_column(
        String(255),
        default="main",
    )

    last_commit: Mapped[str | None] = mapped_column(
        String(64),
    )

    git_status: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )
    indexed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    indexing_in_progress: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    index_version: Mapped[int] = mapped_column(
        default=1,
    )
    sync_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    sync_status: Mapped[str] = mapped_column(
        String(50),
        default="idle",
    )
    open_files: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    recent_files: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    active_file: Mapped[str | None] = mapped_column(
        String(2048),
    )
    workspace_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    last_scan_summary: Mapped[str | None] = mapped_column(
        String(2000),
    )
    owner = relationship(
        "User",
        back_populates="workspaces",
    )

    project = relationship(
        "Project",
        back_populates="workspaces",
    )


    @property
    def is_ready(self) -> bool:
        return (
            self.indexed
            and not self.indexing_in_progress
        )

    @property
    def repository_root(self) -> str:
        return self.root_directory or self.path
Index(
    "idx_workspace_project",
    Workspace.project_id,
)

Index(
    "idx_workspace_owner",
    Workspace.owner_id,
)

Index(
    "idx_workspace_path",
    Workspace.path,
)

Index(
    "idx_workspace_branch",
    Workspace.current_branch,
)

Index(
    "idx_workspace_sync",
    Workspace.sync_status,
)

Index(
    "idx_workspace_indexed",
    Workspace.indexed,
)