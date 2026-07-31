# LLM Manager
from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from .cache import LLMCache
from .exceptions import (
    ContextWindowExceededError,
    NoAvailableProviderError,
)
from .prompts import PromptBuilder
from .provider import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
)
from .registry import LLMRegistry
from .router import (
    LLMRouter,
    RouteRequest,
    TaskType,
)
from .streaming import StreamController
from .tokenizer import Tokenizer

logger = logging.getLogger(__name__)


class LLMManager:
    """
    High-level LLM orchestration layer.

    Responsibilities:
    - Provider routing
    - Cache management
    - Prompt rendering
    - Token validation
    - Standard chat
    - Streaming
    """

    def __init__(
        self,
        *,
        registry: LLMRegistry,
        router: LLMRouter,
        tokenizer: Tokenizer,
        prompt_builder: PromptBuilder,
        cache: LLMCache | None = None,
    ) -> None:

        self.registry = registry
        self.router = router
        self.tokenizer = tokenizer
        self.prompt_builder = prompt_builder
        self.cache = cache or LLMCache()

    # ---------------------------------------------------------
    # Chat
    # ---------------------------------------------------------

    async def chat(
        self,
        *,
        task: TaskType,
        messages: list[ChatMessage],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        use_cache: bool = True,
    ) -> ChatResponse:
        """
        Standard non-streaming completion.
        """

        prepared_messages = self.tokenizer.prepare_messages(
            messages
        )

        prompt_tokens = self.tokenizer.count_messages(
            prepared_messages
        )

        if self.tokenizer.context.exceeds_context(
            prompt_tokens
        ):
            raise ContextWindowExceededError(
                "Prompt exceeds model context window."
            )

        llm = await self.router.route(
            RouteRequest(
                task=task,
                model=model,
                preferred_provider=provider,
            )
        )

        request = ChatRequest(
            model=model or llm.model,
            messages=prepared_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        if use_cache:
            cached = await self.cache.get(request)

            if cached:
                logger.debug("LLM cache hit.")
                return cached

        response = await llm.chat(request)

        if use_cache:
            await self.cache.set(
                request,
                response,
            )

        return response

    # ---------------------------------------------------------
    # Streaming
    # ---------------------------------------------------------

    async def stream(
        self,
        *,
        task: TaskType,
        messages: list[ChatMessage],
        model: str | None = None,
        provider: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """
        Streaming completion.
        """

        llm = await self.router.route(
            RouteRequest(
                task=task,
                model=model,
                preferred_provider=provider,
                require_streaming=True,
            )
        )

        request = ChatRequest(
            model=model or llm.model,
            messages=self.tokenizer.prepare_messages(
                messages
            ),
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        controller = StreamController(
            model=request.model,
        )

        stream: AsyncIterator = llm.stream(
            request
        )

        return await controller.consume(
            stream
        )

    # ---------------------------------------------------------
    # Prompt Helpers
    # ---------------------------------------------------------

    async def execute_prompt(
        self,
        *,
        prompt_name: str,
        task: TaskType,
        variables: dict[str, str],
        system_prompt: str | None = None,
    ) -> ChatResponse:
        """
        Render a registered prompt and execute it.
        """

        prompt = self.prompt_builder.build(
            prompt_name,
            **variables,
        )

        messages: list[ChatMessage] = []

        if system_prompt:
            messages.append(
                ChatMessage(
                    role="system",
                    content=system_prompt,
                )
            )

        messages.append(
            ChatMessage(
                role="user",
                content=prompt,
            )
        )

        return await self.chat(
            task=task,
            messages=messages,
        )

    # ---------------------------------------------------------
    # Embeddings
    # ---------------------------------------------------------

    async def embeddings(
        self,
        texts: list[str],
        *,
        provider: str | None = None,
    ) -> list[list[float]]:
        """
        Generate embeddings.
        """

        if provider:
            llm = self.registry.get(provider)
        else:
            llm = await self.router.route(
                RouteRequest(
                    task=TaskType.EMBEDDING,
                )
            )

        return await llm.embeddings(texts)

    # ---------------------------------------------------------
    # Health
    # ---------------------------------------------------------

    async def healthy_providers(
        self,
    ) -> list[str]:
        return await self.registry.healthy_providers()

    async def available_models(
        self,
        provider: str | None = None,
    ) -> list[str]:
        return await self.registry.available_models(
            provider
        )

    # ---------------------------------------------------------
    # Cache
    # ---------------------------------------------------------

    async def clear_cache(
        self,
    ) -> None:
        await self.cache.clear()

    async def cache_statistics(
        self,
    ):
        return await self.cache.statistics()

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    async def default_provider(self):
        """
        Return the configured default provider.
        """

        name = self.registry.default_provider

        if name is None:
            raise NoAvailableProviderError(
                "No default provider configured."
            )

        return self.registry.get(name)

