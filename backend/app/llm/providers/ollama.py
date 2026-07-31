# Ollama Provider
from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from app.llm.exceptions import (
    ProviderAuthenticationError,
    ProviderConnectionError,
    ProviderError,
    ProviderTimeoutError,
)
from app.llm.provider import (
    BaseLLMProvider,
    ChatRequest,
    ChatResponse,
    ChatMessage,
    StreamChunk,
    FinishReason,
    TokenUsage,
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama implementation.

    Supports:
    - Chat
    - Streaming
    - Embeddings
    - Health Check
    - Model Discovery
    """

    def __init__(
        self,
        *,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout: float = 120,
    ) -> None:

        super().__init__(model=model)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    @property
    def provider_name(self) -> str:
        return "ollama"

    # ---------------------------------------------------------

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:

        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": m.role.value,
                    "content": m.content,
                }
                for m in request.messages
            ],
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        try:

            response = await self.client.post(
                "/api/chat",
                json=payload,
            )

            response.raise_for_status()

        except httpx.ConnectError as e:
            raise ProviderConnectionError(str(e))

        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(str(e))

        except httpx.HTTPStatusError as e:

            if e.response.status_code == 401:
                raise ProviderAuthenticationError()

            raise ProviderError(str(e))

        data = response.json()

        message = ChatMessage(
            role="assistant",
            content=data["message"]["content"],
        )

        usage = TokenUsage(
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get(
                "eval_count",
                0,
            ),
            total_tokens=(
                data.get("prompt_eval_count", 0)
                + data.get("eval_count", 0)
            ),
        )

        return ChatResponse(
            model=request.model,
            message=message,
            finish_reason=FinishReason.STOP,
            usage=usage,
        )

    # ---------------------------------------------------------

    async def stream(
        self,
        request: ChatRequest,
    ) -> AsyncIterator[StreamChunk]:

        payload = {
            "model": request.model,
            "messages": [
                {
                    "role": m.role.value,
                    "content": m.content,
                }
                for m in request.messages
            ],
            "stream": True,
            "options": {
                "temperature": request.temperature,
            },
        }

        async with self.client.stream(
            "POST",
            "/api/chat",
            json=payload,
        ) as response:

            async for line in response.aiter_lines():

                if not line:
                    continue

                obj = json.loads(line)

                done = obj.get("done", False)

                yield StreamChunk(
                    content=obj.get(
                        "message",
                        {},
                    ).get(
                        "content",
                        "",
                    ),
                    done=done,
                )

                if done:
                    break

    # ---------------------------------------------------------

    async def embeddings(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        vectors = []

        for text in texts:

            response = await self.client.post(
                "/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )

            response.raise_for_status()

            vectors.append(
                response.json()["embedding"]
            )

        return vectors

    # ---------------------------------------------------------

    async def health_check(
        self,
    ) -> bool:

        try:

            response = await self.client.get(
                "/api/tags"
            )

            return response.status_code == 200

        except Exception:

            return False

    # ---------------------------------------------------------

    async def available_models(
        self,
    ) -> list[str]:

        response = await self.client.get(
            "/api/tags"
        )

        response.raise_for_status()

        data = response.json()

        return [
            model["name"]
            for model in data.get(
                "models",
                [],
            )
        ]

    # ---------------------------------------------------------

    async def close(
        self,
    ) -> None:

        await self.client.aclose()