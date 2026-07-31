# Gemini Provider
from __future__ import annotations

from typing import Any

from google import genai

from app.llm.provider import (
    ChatRequest,
    BaseLLMProvider,
    ToolDefinition,
)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini Provider.

    Supports:
        - Chat
        - Streaming
        - Tool Calling
        - Vision
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

        self.client = genai.Client(
            api_key=api_key,
        )

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _build_contents(
        self,
        request: ChatRequest,
    ) -> list[dict[str, Any]]:

        contents = []

        for message in request.messages:

            if message.role == "system":
                continue

            contents.append(
                {
                    "role": message.role,
                    "parts": [
                        {
                            "text": message.content,
                        }
                    ],
                }
            )

        return contents

    def _system_instruction(
        self,
        request: ChatRequest,
    ) -> str | None:

        for message in request.messages:

            if message.role == "system":

                return message.content

        return None

    def _build_tools(
        self,
        request: ChatRequest,
    ):

        if not request.tools:

            return None

        tools = []

        for tool in request.tools:

            tools.append(
                self._convert_tool(tool)
            )

        return tools

    def _convert_tool(
        self,
        tool: ToolDefinition,
    ):

        return {

            "function_declarations": [

                {

                    "name": tool.name,

                    "description": tool.description,

                    "parameters": tool.parameters,

                }

            ]
        }

    def _build_request(
        self,
        request: ChatRequest,
    ):

        payload = {

            "model": request.model,

            "contents":
                self._build_contents(request),
        }

        system = self._system_instruction(
            request,
        )

        if system:

            payload[
                "system_instruction"
            ] = system

        tools = self._build_tools(
            request,
        )

        if tools:

            payload["tools"] = tools

        return payload

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        try:

            payload = self._build_request(
                request,
            )

            response = await self.client.aio.models.generate_content(
                **payload,
            )

            return self._parse_response(
                response,
            )

        except Exception as exc:

            raise self._map_error(
                exc,
            )
    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:

        payload = self._build_request(
            request,
        )

        try:

            async for chunk in self.client.aio.models.generate_content_stream(
                **payload,
            ):

                text = ""

                if (
                    hasattr(chunk, "text")
                    and chunk.text
                ):
                    text = chunk.text

                if text:

                    yield StreamChunk(
                        content=text,
                        finished=False,
                    )

            yield StreamChunk(
                content="",
                finished=True,
            )

        except Exception as exc:

            raise self._map_error(
                exc,
            )

    def _parse_response(
        self,
        response,
    ) -> ChatResponse:

        text = ""

        tool_calls = []

        if hasattr(response, "text"):

            text = response.text or ""

        tool_calls.extend(
            self._parse_tool_calls(
                response,
            )
        )

        return ChatResponse(

            content=text,

            tool_calls=tool_calls,

            usage=self._parse_usage(
                response,
            ),

            model=getattr(
                response,
                "model_version",
                None,
            ),

            finish_reason=getattr(
                response,
                "finish_reason",
                None,
            ),
        )
    def _parse_tool_calls(
        self,
        response,
    ) -> list[ToolCall]:

        tool_calls = []

        candidates = getattr(
            response,
            "candidates",
            [],
        )

        for candidate in candidates:

            content = getattr(
                candidate,
                "content",
                None,
            )

            if content is None:
                continue

            parts = getattr(
                content,
                "parts",
                [],
            )

            for part in parts:

                function_call = getattr(
                    part,
                    "function_call",
                    None,
                )

                if function_call is None:
                    continue

                tool_calls.append(

                    ToolCall(

                        id=function_call.name,

                        name=function_call.name,

                        arguments=function_call.args,
                    )
                )

        return tool_calls

    def _parse_usage(
        self,
        response,
    ):

        usage = getattr(
            response,
            "usage_metadata",
            None,
        )

        if usage is None:

            return None

        return {

            "prompt_tokens":
                getattr(
                    usage,
                    "prompt_token_count",
                    0,
                ),

            "completion_tokens":
                getattr(
                    usage,
                    "candidates_token_count",
                    0,
                ),

            "total_tokens":
                getattr(
                    usage,
                    "total_token_count",
                    0,
                ),
        }

from app.llm.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
    RateLimitError,
)


async def embeddings(
    self,
    texts: list[str],
    model: str = "text-embedding-004",
):

    try:

        vectors = []

        for text in texts:

            response = await self.client.aio.models.embed_content(

                model=model,

                contents=text,
            )

            vectors.append(
                response.embeddings[0].values
            )

        return vectors

    except Exception as exc:

        raise self._map_error(exc)

async def health_check(
    self,
) -> bool:

    try:

        await self.client.aio.models.generate_content(

            model="gemini-2.5-flash",

            contents="ping",
        )

        return True

    except Exception:

        return False

async def available_models(
    self,
) -> list[str]:

    return [

        "gemini-2.5-pro",

        "gemini-2.5-flash",

        "gemini-2.5-flash-lite",

        "text-embedding-004",
    ]

def _map_error(
    self,
    error: Exception,
) -> Exception:

    message = str(error).lower()

    if "authentication" in message:

        return ProviderAuthenticationError(
            str(error)
        )

    if "unauthorized" in message:

        return ProviderAuthenticationError(
            str(error)
        )

    if "429" in message:

        return RateLimitError(
            str(error)
        )

    if "timeout" in message:

        return ProviderTimeoutError(
            str(error)
        )

    if "connection" in message:

        return ProviderConnectionError(
            str(error)
        )

    return ProviderError(
        str(error)
    )

async def close(
    self,
) -> None:
    """
    Close provider resources.

    The current google-genai client
    does not require explicit cleanup.
    """

    return

