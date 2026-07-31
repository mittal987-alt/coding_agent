# LLM Response
from __future__ import annotations

from typing import Any

from .exceptions import (
    EmptyResponseError,
    InvalidResponseFormatError,
)
from .provider import (
    ChatMessage,
    ChatResponse,
    FinishReason,
    MessageRole,
    StreamChunk,
    TokenUsage,
    ToolCall,
)


class ResponseParser:
    """
    Parses provider-specific responses into unified ChatResponse objects.
    """

    @staticmethod
    def validate(response: ChatResponse) -> None:
        """
        Validate a parsed response.
        """

        if response.message is None:
            raise EmptyResponseError("Response contains no message.")

        if response.message.content is None and not response.message.tool_calls:
            raise InvalidResponseFormatError(
                "Response contains neither text nor tool calls."
            )

    @staticmethod
    def normalize_finish_reason(
        reason: str | None,
    ) -> FinishReason:
        """
        Normalize provider-specific finish reasons.
        """

        mapping = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "tool_calls": FinishReason.TOOL_CALL,
            "tool_call": FinishReason.TOOL_CALL,
            "content_filter": FinishReason.CONTENT_FILTER,
            "error": FinishReason.ERROR,
            None: FinishReason.STOP,
        }

        return mapping.get(reason, FinishReason.STOP)

    @staticmethod
    def build_usage(
        *,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
    ) -> TokenUsage:

        return TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    @staticmethod
    def assistant_message(
        content: str,
    ) -> ChatMessage:

        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content=content,
        )

    @staticmethod
    def tool_message(
        tool_calls: list[ToolCall],
    ) -> ChatMessage:

        return ChatMessage(
            role=MessageRole.ASSISTANT,
            content="",
            tool_calls=tool_calls,
        )

    @classmethod
    def build_response(
        cls,
        *,
        model: str,
        content: str,
        finish_reason: str | None = None,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        tool_calls: list[ToolCall] | None = None,
        raw_response: dict[str, Any] | None = None,
    ) -> ChatResponse:

        tool_calls = tool_calls or []

        if tool_calls:
            message = cls.tool_message(tool_calls)
        else:
            message = cls.assistant_message(content)

        response = ChatResponse(
            model=model,
            message=message,
            finish_reason=cls.normalize_finish_reason(
                finish_reason
            ),
            usage=cls.build_usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            ),
            raw_response=raw_response or {},
        )

        cls.validate(response)

        return response


class StreamResponseBuilder:
    """
    Incrementally constructs a streamed response.
    """

    def __init__(self) -> None:

        self._content: list[str] = []

        self._tool_calls: list[ToolCall] = []

        self._finish_reason: FinishReason | None = None

    def add_chunk(
        self,
        chunk: StreamChunk,
    ) -> None:

        if chunk.content:
            self._content.append(chunk.content)

        if chunk.tool_calls:
            self._tool_calls.extend(chunk.tool_calls)

        if chunk.finish_reason is not None:
            self._finish_reason = chunk.finish_reason

    def build(
        self,
        *,
        model: str,
    ) -> ChatResponse:

        message = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="".join(self._content),
            tool_calls=self._tool_calls,
        )

        response = ChatResponse(
            model=model,
            message=message,
            finish_reason=self._finish_reason
            or FinishReason.STOP,
        )

        ResponseParser.validate(response)

        return response