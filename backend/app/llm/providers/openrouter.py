# OpenRouter Provider
from __future__ import annotations

from typing import Any, AsyncIterator

from openai import (
    AsyncOpenAI,
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    RateLimitError as OpenAIRateLimitError,
)

from app.llm.exceptions import (
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


class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter Provider.

    Supports

    - Chat
    - Streaming
    - Tool Calling
    - Vision
    - Structured Outputs
    """

    def __init__(
        self,
        api_key: str,
        *,
        app_name: str = "AI Software Engineer",
        site_url: str = "http://localhost",
        timeout: float = 120.0,
    ) -> None:

        super().__init__(model="")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=timeout,
        )

        self.app_name = app_name
        self.site_url = site_url

    @property
    def provider_name(self) -> str:
        return "openrouter"

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------

    def _extra_headers(self) -> dict[str, str]:
        return {
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
        }

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
    ) -> list[dict[str, Any]] | None:

        if not request.tools:
            return None

        return [self._convert_tool(tool) for tool in request.tools]

    def _convert_tool(
        self,
        tool: ToolDefinition,
    ) -> dict[str, Any]:

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
    ) -> dict[str, Any]:

        payload: dict[str, Any] = {
            "model": request.model,
            "messages": self._build_messages(request),
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "extra_headers": self._extra_headers(),
        }

        tools = self._build_tools(request)

        if tools:
            payload["tools"] = tools

        if request.top_p is not None:
            payload["top_p"] = request.top_p

        if request.stop:
            payload["stop"] = request.stop

        return payload

    def _parse_tool_calls(
        self,
        message,
    ) -> list[ToolCall]:

        tool_calls: list[ToolCall] = []

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

    def _parse_usage(self, response) -> TokenUsage:

        usage = getattr(response, "usage", None)

        if usage is None:
            return TokenUsage()

        return TokenUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", 0),
            completion_tokens=getattr(usage, "completion_tokens", 0),
            total_tokens=getattr(usage, "total_tokens", 0),
        )

    def _parse_response(self, response) -> ChatResponse:

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

    def _map_error(self, exc: Exception) -> Exception:

        if isinstance(exc, AuthenticationError):
            return ProviderAuthenticationError(str(exc))

        if isinstance(exc, APITimeoutError):
            return ProviderTimeoutError(str(exc))

        if isinstance(exc, APIConnectionError):
            return ProviderConnectionError(str(exc))

        if isinstance(exc, OpenAIRateLimitError):
            return RateLimitError(str(exc))

        return ProviderError(str(exc))

    # ----------------------------------------------------------------
    # Core Interface
    # ----------------------------------------------------------------

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        try:

            payload = self._build_request(request)

            response = await self.client.chat.completions.create(**payload)

            return self._parse_response(response)

        except Exception as exc:
            raise self._map_error(exc)

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:

        payload = self._build_request(request)
        payload["stream"] = True

        try:

            stream = await self.client.chat.completions.create(**payload)

            async for chunk in stream:

                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                if delta.content:
                    yield StreamChunk(content=delta.content)

            yield StreamChunk(content="", finish_reason=FinishReason.STOP)

        except Exception as exc:
            raise self._map_error(exc)

    async def embeddings(
        self,
        texts: list[str],
        model: str = "openai/text-embedding-3-small",
    ) -> list[list[float]]:

        try:

            response = await self.client.embeddings.create(
                model=model,
                input=texts,
                extra_headers=self._extra_headers(),
            )

            return [item.embedding for item in response.data]

        except Exception as exc:
            raise self._map_error(exc)

    async def health_check(self) -> bool:

        try:

            await self.client.chat.completions.create(
                model="openai/gpt-4.1-mini",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1,
                extra_headers=self._extra_headers(),
            )

            return True

        except Exception:
            return False

    async def available_models(self) -> list[str]:

        return [
            "openai/gpt-4.1",
            "openai/gpt-4.1-mini",
            "anthropic/claude-3.7-sonnet",
            "google/gemini-2.5-pro",
            "google/gemini-2.5-flash",
            "mistralai/mistral-large",
            "meta-llama/llama-3.3-70b-instruct",
            "deepseek/deepseek-chat",
            "qwen/qwen-3-235b",
            "openai/text-embedding-3-small",
        ]

    async def close(self) -> None:
        """
        Close underlying HTTP resources.
        """
        if hasattr(self.client, "close"):
            await self.client.close()
