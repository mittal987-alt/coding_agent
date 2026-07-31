from __future__ import annotations

from typing import Any, AsyncIterator

from anthropic import (
    AsyncAnthropic,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError as AnthropicRateLimitError,
)
from anthropic.types import Message

from app.llm.provider import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    BaseLLMProvider,
    ToolDefinition,
    ToolCall,
    StreamChunk,
)
from app.llm.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
    UnsupportedModelError,
)

class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude Provider.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        super().__init__(model="")
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout
        self.client = AsyncAnthropic(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
        )

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _build_messages(self, request: ChatRequest) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = []
        for message in request.messages:
            if message.role == "system":
                continue
            messages.append({"role": message.role, "content": message.content})
        return messages

    def _system_prompt(self, request: ChatRequest) -> str | None:
        for message in request.messages:
            if message.role == "system":
                return message.content
        return None

    def _build_tools(self, request: ChatRequest) -> list[dict[str, Any]] | None:
        if not request.tools:
            return None
        return [self._convert_tool(tool) for tool in request.tools]

    def _convert_tool(self, tool: ToolDefinition) -> dict[str, Any]:
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.parameters,
        }

    def _build_request(self, request: ChatRequest) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": self._build_messages(request),
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
        }
        system = self._system_prompt(request)
        if system:
            payload["system"] = system
        tools = self._build_tools(request)
        if tools:
            payload["tools"] = tools
        if request.stop:
            payload["stop_sequences"] = request.stop
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        return payload

    async def chat(self, request: ChatRequest) -> ChatResponse:
        try:
            payload = self._build_request(request)
            response: Message = await self.client.messages.create(**payload)
            return self._parse_response(response)
        except Exception as exc:
            raise self._map_error(exc)

    async def stream(self, request: ChatRequest) -> AsyncIterator[StreamChunk]:
        payload = self._build_request(request)
        payload["stream"] = True
        try:
            async with self.client.messages.stream(**payload) as stream:
                async for event in stream:
                    if event.type == "content_block_delta":
                        delta = getattr(event.delta, "text", None)
                        if delta:
                            yield StreamChunk(content=delta, finished=False)
                final = await stream.get_final_message()
                yield StreamChunk(
                    content="",
                    finished=True,
                    usage=self._parse_usage(final),
                )
        except Exception as exc:
            raise self._map_error(exc)

    def _parse_response(self, response: Message) -> ChatResponse:
        text = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text += block.text
            elif block.type == "tool_use":
                tool_calls.append(self._parse_tool(block))
        return ChatResponse(
            content=text,
            tool_calls=tool_calls,
            usage=self._parse_usage(response),
            model=response.model,
            finish_reason=response.stop_reason,
        )

    def _parse_tool(self, block) -> ToolCall:
        return ToolCall(
            id=block.id,
            name=block.name,
            arguments=block.input,
        )

    def _parse_usage(self, response: Message):
        if not hasattr(response, "usage"):
            return None
        return {
            "input_tokens": getattr(response.usage, "input_tokens", 0),
            "output_tokens": getattr(response.usage, "output_tokens", 0),
        }

    async def health_check(self) -> bool:
        try:
            await self.client.messages.create(
                model="claude-3-5-haiku-latest",
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False

    async def available_models(self) -> list[str]:
        return [
            "claude-3-5-haiku-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-7-sonnet-latest",
            "claude-opus-4-0",
        ]

    async def embeddings(self, texts: list[str], model: str | None = None):
        raise UnsupportedModelError("Anthropic currently does not provide an embeddings API.")

    def _map_error(self, error: Exception) -> Exception:
        if isinstance(error, AuthenticationError):
            return ProviderAuthenticationError(str(error))
        if isinstance(error, AnthropicRateLimitError):
            return RateLimitError(str(error))
        if isinstance(error, APIConnectionError):
            return ProviderConnectionError(str(error))
        if isinstance(error, APITimeoutError):
            return ProviderTimeoutError(str(error))
        return ProviderError(str(error))

    async def close(self) -> None:
        return
