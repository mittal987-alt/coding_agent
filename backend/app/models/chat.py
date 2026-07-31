from __future__ import annotations

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Entity

class Chat(Entity):
    """
    AI conversation session.
    """

    __tablename__ = "chats"

    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    project_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
    )

    system_prompt: Mapped[str | None] = mapped_column(
        Text,
    )
    model_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    temperature: Mapped[float] = mapped_column(
        default=0.2,
    )
    prompt_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    completion_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    is_streaming: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    conversation_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    context_files: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )
    user = relationship(
        "User",
        back_populates="chats",
    )

    project = relationship(
        "Project",
        back_populates="chats",
    )


    messages = relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
    )
    @property
    def token_usage(self) -> dict:

        return {
            "prompt": self.prompt_tokens,
            "completion": self.completion_tokens,
            "total": self.total_tokens,
        }

    @property
    def is_active(self) -> bool:

        return (
            not self.archived
            and not self.is_deleted
        )
Index(
    "idx_chat_user",
    Chat.user_id,
)

Index(
    "idx_chat_project",
    Chat.project_id,
)

Index(
    "idx_chat_model",
    Chat.model_name,
)

Index(
    "idx_chat_provider",
    Chat.provider,
)

Index(
    "idx_chat_archived",
    Chat.archived,
)

Index(
    "idx_chat_pinned",
    Chat.pinned,
)


class ChatMessage(Entity):
    """
    AI conversation message.
    """

    __tablename__ = "chat_messages"

    chat_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tool_call_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    message_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        default=dict,
    )

    chat = relationship(
        "Chat",
        back_populates="messages",
    )


# Indexes
Index("idx_chat_message_chat", ChatMessage.chat_id)