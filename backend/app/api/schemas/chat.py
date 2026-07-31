#
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.api.schemas.common import (
    BaseSchema,
    TimestampSchema,
)

class TokenUsage(BaseSchema):

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

class ToolCall(BaseSchema):

    id: str

    name: str

    arguments: dict[str, Any]

    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
    ] = "pending"

class ChatResponse(BaseSchema):

    message: str

    model: str

    usage: TokenUsage

    tool_calls: list[ToolCall] = Field(
        default_factory=list,
    )

    finish_reason: str | None = None
class StreamChunk(BaseSchema):

    token: str

    finished: bool = False
class ChatMessage(TimestampSchema):

    role: Literal[
        "system",
        "user",
        "assistant",
        "tool",
    ]

    content: str

    tool_call_id: str | None = None

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

class ConversationHistory(BaseSchema):

    session_id: str

    messages: list[ChatMessage]

class StreamingRequest(ChatRequest):

    stream: bool = True

class ConversationSummary(BaseSchema):

    session_id: str

    title: str

    last_message: str

    updated_at: datetime
class SessionList(BaseSchema):

    sessions: list[ConversationSummary]
class ToolResult(BaseSchema):

    tool: str

    success: bool

    output: Any = None

    error: str | None = None

    execution_time_ms: float
class ChatEvent(BaseSchema):

    event: Literal[
        "message",
        "token",
        "tool_start",
        "tool_end",
        "done",
        "error",
    ]

    data: dict[str, Any]
class ReasoningStep(BaseSchema):

    step: int

    title: str

    description: str

    duration_ms: float
class AgentChatResponse(ChatResponse):

    reasoning: list[ReasoningStep] = Field(
        default_factory=list,
    )

    execution_time_ms: float

    session_id: str