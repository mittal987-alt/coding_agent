from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ConversationRole(str, Enum):
    """Role of a participant in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class MessageType(str, Enum):
    """Type of conversation message."""

    TEXT = "text"
    CODE = "code"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    SUMMARY = "summary"


class ConversationStatus(str, Enum):
    """Conversation lifecycle."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


class ConversationMessage(BaseModel):
    """
    Individual message within a conversation.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    conversation_id: str

    role: ConversationRole

    type: MessageType = MessageType.TEXT

    content: str

    metadata: dict[str, Any] = Field(default_factory=dict)

    tool_name: str | None = None

    tool_arguments: dict[str, Any] | None = None

    tool_result: dict[str, Any] | None = None

    referenced_memory_ids: list[str] = Field(default_factory=list)

    token_count: int = 0

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationSummary(BaseModel):
    """
    Summary of older conversation messages.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    conversation_id: str

    summary: str

    message_count: int

    start_message_id: str | None = None

    end_message_id: str | None = None

    token_count: int = 0

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ContextWindow(BaseModel):
    """
    Context sent to the LLM.
    """

    messages: list[ConversationMessage] = Field(default_factory=list)

    summaries: list[ConversationSummary] = Field(default_factory=list)

    referenced_memories: list[str] = Field(default_factory=list)

    total_tokens: int = 0

    max_tokens: int = 16000

    truncated: bool = False


class Conversation(BaseModel):
    """
    Complete conversation session.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str = "Untitled Conversation"

    user_id: str | None = None

    project_id: str | None = None

    agent_id: str | None = None

    status: ConversationStatus = ConversationStatus.ACTIVE

    messages: list[ConversationMessage] = Field(default_factory=list)

    summaries: list[ConversationSummary] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    total_messages: int = 0

    total_tokens: int = 0

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    last_activity: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ConversationStatistics(BaseModel):
    """
    Conversation analytics.
    """

    conversation_id: str

    total_messages: int

    user_messages: int

    assistant_messages: int

    tool_messages: int

    summaries: int

    total_tokens: int

    average_tokens_per_message: float

    started_at: datetime

    last_activity: datetime