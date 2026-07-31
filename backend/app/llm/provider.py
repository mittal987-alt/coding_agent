# LLM Provider Base
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================


class MessageRole(str, Enum):
    """
    Chat message roles.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FinishReason(str, Enum):
    """
    Completion termination reason.
    """

    STOP = "stop"
    LENGTH = "length"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"


# ============================================================
# Tool Calling
# ============================================================


class ToolDefinition(BaseModel):
    """
    Tool definition exposed to the LLM.
    """

    name: str

    description: str

    parameters: dict[str, Any]


class ToolCall(BaseModel):
    """
    Tool invocation returned by the LLM.
    """

    id: str

    name: str

    arguments: dict[str, Any]


# ============================================================
# Messages
# ============================================================


class ChatMessage(BaseModel):
    """
    Standard chat message.
    """

    role: MessageRole

    content: str

    name: str | None = None

    tool_calls: list[ToolCall] = Field(default_factory=list)


# ============================================================
# Usage
# ============================================================


class TokenUsage(BaseModel):
    """
    Token accounting.
    """

    prompt_tokens: int = 0

    completion_tokens: int = 0

    total_tokens: int = 0


# ============================================================
# Request
# ============================================================


class ChatRequest(BaseModel):
    """
    Unified chat request.
    """

    model: str

    messages: list[ChatMessage]

    temperature: float = 0.2

    max_tokens: int | None = None

    top_p: float = 1.0

    stop: list[str] | None = None

    stream: bool = False

    tools: list[ToolDefinition] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


# ============================================================
# Response
# ============================================================


class ChatResponse(BaseModel):
    """
    Unified LLM response.
    """

    model: str

    message: ChatMessage

    finish_reason: FinishReason = FinishReason.STOP

    usage: TokenUsage = Field(default_factory=TokenUsage)

    raw_response: dict[str, Any] = Field(default_factory=dict)


# ============================================================
# Streaming
# ============================================================


class StreamChunk(BaseModel):
    """
    Partial streamed response.
    """

    content: str = ""

    tool_calls: list[ToolCall] = Field(default_factory=list)

    finish_reason: FinishReason | None = None


# ============================================================
# Provider Interface
# ============================================================


class BaseLLMProvider(ABC):
    """
    Abstract base class implemented by every provider.
    """

    def __init__(
        self,
        model: str,
    ) -> None:
        self.model = model

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Provider identifier.
        """
        ...

    @abstractmethod
    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Standard completion.
        """
        ...

    @abstractmethod
    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:
        """
        Streaming completion.
        """
        ...

    @abstractmethod
    async def embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings.
        """
        ...

    @abstractmethod
    async def health_check(
        self,
    ) -> bool:
        """
        Check provider availability.
        """
        ...

    @abstractmethod
    async def available_models(
        self,
    ) -> list[str]:
        """
        Return supported models.
        """
        ...