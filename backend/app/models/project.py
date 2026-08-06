from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workspace import Workspace
    from app.models.chat import Chat
    from app.models.events import Event
    from app.models.memory import Memory

class Project(BaseModel):
    __tablename__ = "projects"

    owner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    repository_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    default_branch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    github_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str | None] = mapped_column(String(50), nullable=True)
    framework: Mapped[str | None] = mapped_column(String(100), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(String(5000), nullable=True)
    env_vars: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=None)

    # Relationships
    workspaces: Mapped[List["Workspace"]] = relationship("Workspace", back_populates="project", cascade="all, delete-orphan")
    chats: Mapped[List["Chat"]] = relationship("Chat", back_populates="project", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship("Event", back_populates="project", cascade="all, delete-orphan")
    memories: Mapped[List["Memory"]] = relationship("Memory", back_populates="project", cascade="all, delete-orphan")