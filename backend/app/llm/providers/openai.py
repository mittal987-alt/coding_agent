# OpenAI Provider
from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from typing import Any

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError as OpenAIRateLimitError,
)

from app.llm.exceptions import (
    InvalidParameterError,
    ModelNotFoundError,
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
)
from app.llm.provider import (
    BaseLLMProvider,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    FinishReason,
    StreamChunk,
    TokenUsage,
    ToolCall,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    Production OpenAI provider.

    Supports:

    • Chat
    • Streaming
    • Tool Calling
    • Structured Output
    • Embeddings
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        organization: str | None = None,
        project: str | None = None,
        timeout: float = 120,
    ) -> None:

        super().__init__(model=model)

        self.client = AsyncOpenAI(
            api_key=api_key,
            organization=organization,
            project=project,
            timeout=timeout,
        )

    @property
    def provider_name(self) -> str:
        return "openai"

    async def close(self) -> None:
        """
        Close underlying HTTP client.
        """
        await self.client.close()

    # ============================================================
    # Message Helpers
    # ============================================================

    def _build_messages(
        self,
        request: ChatRequest,
    ) -> list[dict[str, Any]]:

        messages = []

        for message in request.messages:
            messages.append(
                {
                    "role": message.role.value,
                    "content": message.content,
                }
            )

        return messages

    def _build_usage(
        self,
        usage: Any,
    ) -> TokenUsage:

        if usage is None:
            return TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            )

        return TokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
        )

    def _finish_reason(
        self,
        reason: str | None,
    ) -> FinishReason:

        mapping = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "tool_calls": FinishReason.TOOL_CALL,
            "content_filter": FinishReason.CONTENT_FILTER,
        }

        return mapping.get(
            reason,
            FinishReason.STOP,
        )

    def _raise_provider_error(
        self,
        exc: Exception,
    ) -> None:

        if isinstance(exc, AuthenticationError):
            raise ProviderAuthenticationError(str(exc))

        if isinstance(exc, APIConnectionError):
            raise ProviderConnectionError(str(exc))

        if isinstance(exc, APITimeoutError):
            raise ProviderTimeoutError(str(exc))

        if isinstance(exc, OpenAIRateLimitError):
            raise RateLimitError(str(exc))

        if isinstance(exc, PermissionDeniedError):
            raise ProviderAuthenticationError(str(exc))

        if isinstance(exc, NotFoundError):
            raise ModelNotFoundError(str(exc))

        if isinstance(exc, BadRequestError):
            raise InvalidParameterError(str(exc))

        if isinstance(exc, InternalServerError):
            raise ProviderError(str(exc))

        raise ProviderError(str(exc))

    def _build_response(
        self,
        response,
    ) -> ChatResponse:

        choice = response.choices[0]

        tool_calls = self._parse_tool_calls(choice.message)

        message = ChatMessage(
            role="assistant",
            content=choice.message.content or "",
            tool_calls=tool_calls,
        )

        return ChatResponse(
            model=response.model,
            message=message,
            finish_reason=self._finish_reason(choice.finish_reason),
            usage=self._build_usage(response.usage),
        )

    # ============================================================
    # Tool Conversion
    # ============================================================

    def _build_tools(
        self,
        tools: list[ToolDefinition] | None,
    ) -> list[dict[str, Any]] | None:
        """
        Convert internal ToolDefinition objects into the OpenAI tool schema.
        """

        if not tools:
            return None

        result = []

        for tool in tools:
            result.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
            )

        return result

    # ============================================================
    # Parse Tool Calls
    # ============================================================

    def _parse_tool_calls(
        self,
        message,
    ) -> list[ToolCall]:

        if not getattr(message, "tool_calls", None):
            return []

        calls = []

        for tool in message.tool_calls:
            calls.append(
                ToolCall(
                    id=tool.id,
                    name=tool.function.name,
                    arguments=tool.function.arguments,
                )
            )

        return calls

    # ============================================================
    # Chat
    # ============================================================

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Execute a standard chat completion.
        """

        try:

            response = await self.client.chat.completions.create(
                model=request.model,
                messages=self._build_messages(request),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                tools=self._build_tools(request.tools) if request.tools else None,
                tool_choice="auto" if request.tools else None,
            )

            return self._build_response(response)

        except Exception as exc:
            self._raise_provider_error(exc)

    # ============================================================
    # Streaming
    # ============================================================

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:
        """
        Stream responses from OpenAI.
        """

        try:

            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=self._build_messages(request),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
                tools=self._build_tools(request.tools) if request.tools else None,
            )

            async for event in stream:

                if not event.choices:
                    continue

                delta = event.choices[0].delta

                content = delta.content or ""

                finish = event.choices[0].finish_reason is not None

                yield StreamChunk(
                    content=content,
                    finish_reason=self._finish_reason(event.choices[0].finish_reason) if finish else None,
                )

        except Exception as exc:
            self._raise_provider_error(exc)

    # ============================================================
    # Embeddings
    # ============================================================

    async def embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate vector embeddings.
        """

        try:

            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts,
            )

            return [item.embedding for item in response.data]

        except Exception as exc:
            self._raise_provider_error(exc)

    # ============================================================
    # Available Models
    # ============================================================

    async def available_models(
        self,
    ) -> list[str]:

        try:

            response = await self.client.models.list()

            return sorted(model.id for model in response.data)

        except Exception as exc:
            self._raise_provider_error(exc)

    # ============================================================
    # Health Check
    # ============================================================

    async def health_check(
        self,
    ) -> bool:
        """
        Verify provider availability.
        """

        try:

            await self.client.models.list()

            return True

        except APIStatusError as exc:

            logger.warning(
                "OpenAI health check failed: %s",
                exc,
            )

            return False

        except Exception:

            return False

    # ============================================================
    # Structured Output
    # ============================================================

    async def structured_chat(
        self,
        request: ChatRequest,
        schema: dict[str, Any],
    ) -> ChatResponse:
        """
        Request structured JSON output.
        """

        try:

            response = await self.client.chat.completions.create(
                model=request.model,
                messages=self._build_messages(request),
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "response",
                        "schema": schema,
                    },
                },
            )

            return self._build_response(response)

        except Exception as exc:
            self._raise_provider_error(exc)

    # ============================================================
    # Reasoning Models
    # ============================================================

    def supports_reasoning(
        self,
    ) -> bool:

        return (
            self.model.startswith("o")
            or "reason" in self.model.lower()
        )