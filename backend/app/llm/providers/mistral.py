# Mistral Provider
from __future__ import annotations

from typing import Any, AsyncIterator

from mistralai.client import Mistral

from app.llm.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
)
from app.llm.provider import (
    BaseLLMProvider,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    FinishReason,
    StreamChunk,
    TokenUsage,
    ToolCall,
    ToolDefinition,
)


class MistralProvider(BaseLLMProvider):
    """
    Mistral AI Provider.

    Supports

    - Chat
    - Streaming
    - Tool Calling
    - Embeddings
    """

    def __init__(
        self,
        api_key: str,
        *,
        timeout: float = 120.0,
        base_url: str | None = None,
    ) -> None:

        super().__init__(model="")

        self.api_key = api_key
        self.timeout = timeout
        self.base_url = base_url

        self.client = Mistral(
            api_key=api_key,
            timeout_ms=int(timeout * 1000),
        )

    @property
    def provider_name(self) -> str:
        return "mistral"

    def _build_messages(
        self,
        request: ChatRequest,
    ) -> list[dict[str, Any]]:

        messages = []

        for message in request.messages:
            messages.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )

        return messages

    def _build_tools(
        self,
        request: ChatRequest,
    ):

        if not request.tools:
            return None

        tools = []

        for tool in request.tools:
            tools.append(self._convert_tool(tool))

        return tools

    def _convert_tool(
        self,
        tool: ToolDefinition,
    ):

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            },
        }

    def _build_request(
        self,
        request: ChatRequest,
    ):

        payload = {
            "model": request.model,
            "messages": self._build_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        tools = self._build_tools(request)

        if tools:
            payload["tools"] = tools

        if request.top_p is not None:
            payload["top_p"] = request.top_p

        if request.stop:
            payload["stop"] = request.stop

        return payload

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        try:

            payload = self._build_request(request)

            response = await self.client.chat.complete_async(**payload)

            return self._parse_response(response)

        except Exception as exc:

            raise self._map_error(exc)

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:

        payload = self._build_request(request)

        try:

            stream = await self.client.chat.stream_async(**payload)

            async for event in stream:

                if not event.data.choices:
                    continue

                delta = event.data.choices[0].delta.content

                if delta:
                    yield StreamChunk(content=delta)

            yield StreamChunk(content="", finish_reason=FinishReason.STOP)

        except Exception as exc:

            raise self._map_error(exc)

    def _parse_response(
        self,
        response,
    ) -> ChatResponse:

        choice = response.choices[0]
        message = choice.message
        tool_calls = self._parse_tool_calls(message)

        return ChatResponse(
            model=response.model,
            message=ChatMessage(
                role="assistant",
                content=message.content or "",
                tool_calls=tool_calls,
            ),
            usage=self._parse_usage(response),
            finish_reason=FinishReason.STOP,
        )

    def _parse_tool_calls(
        self,
        message,
    ) -> list[ToolCall]:

        tool_calls = []

        if not getattr(message, "tool_calls", None):
            return tool_calls

        for tool in message.tool_calls:
            function = tool.function
            tool_calls.append(
                ToolCall(
                    id=tool.id,
                    name=function.name,
                    arguments=function.arguments,
                )
            )

        return tool_calls

    def _parse_usage(
        self,
        response,
    ) -> TokenUsage:

        usage = getattr(response, "usage", None)

        if usage is None:
            return TokenUsage()

        return TokenUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", 0),
            completion_tokens=getattr(usage, "completion_tokens", 0),
            total_tokens=getattr(usage, "total_tokens", 0),
        )

    async def embeddings(
        self,
        texts: list[str],
        model: str = "mistral-embed",
    ) -> list[list[float]]:

        try:

            response = await self.client.embeddings.create_async(
                model=model,
                inputs=texts,
            )

            return [embedding.embedding for embedding in response.data]

        except Exception as exc:

            raise self._map_error(exc)

    async def health_check(
        self,
    ) -> bool:

        try:

            await self.client.chat.complete_async(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
            )

            return True

        except Exception:

            return False

    async def available_models(
        self,
    ) -> list[str]:

        return [
            "mistral-small-latest",
            "mistral-medium-latest",
            "mistral-large-latest",
            "codestral-latest",
            "mistral-embed",
        ]

    def _map_error(
        self,
        error: Exception,
    ) -> Exception:

        message = str(error).lower()

        if "authentication" in message or "unauthorized" in message:
            return ProviderAuthenticationError(str(error))

        if "429" in message:
            return RateLimitError(str(error))

        if "timeout" in message:
            return ProviderTimeoutError(str(error))

        if "connection" in message:
            return ProviderConnectionError(str(error))

        return ProviderError(str(error))

    async def close(
        self,
    ) -> None:
        """
        Close provider resources.

        Current Mistral SDK manages its own HTTP client lifecycle.
        """
        return