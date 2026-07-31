# LLM Router
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

from .exceptions import (
    NoAvailableProviderError,
    RoutingError,
)
from .provider import BaseLLMProvider
from .registry import LLMRegistry

logger = logging.getLogger(__name__)


# ============================================================
# Task Types
# ============================================================


class TaskType(str, Enum):
    CHAT = "chat"
    CODING = "coding"
    PLANNING = "planning"
    REVIEW = "review"
    DEBUGGING = "debugging"
    EMBEDDING = "embedding"
    SUMMARIZATION = "summarization"
    REASONING = "reasoning"


# ============================================================
# Route Request
# ============================================================


@dataclass(slots=True)
class RouteRequest:
    """
    Information used to select the best provider.
    """

    task: TaskType

    model: str | None = None

    preferred_provider: str | None = None

    require_streaming: bool = False

    require_tools: bool = False

    max_cost: float | None = None

    max_latency_ms: int | None = None


# ============================================================
# Router
# ============================================================


class LLMRouter:
    """
    Intelligent routing layer.

    Chooses the best provider for each request.
    """

    def __init__(
        self,
        registry: LLMRegistry,
    ) -> None:

        self.registry = registry

        self._task_preferences: dict[
            TaskType,
            list[str],
        ] = {
            TaskType.CODING: [
                "anthropic",
                "openai",
                "mistral",
                "ollama",
            ],
            TaskType.DEBUGGING: [
                "anthropic",
                "openai",
                "ollama",
            ],
            TaskType.PLANNING: [
                "anthropic",
                "openai",
                "gemini",
            ],
            TaskType.REVIEW: [
                "anthropic",
                "openai",
            ],
            TaskType.CHAT: [
                "openai",
                "gemini",
                "anthropic",
            ],
            TaskType.SUMMARIZATION: [
                "gemini",
                "openai",
                "mistral",
            ],
            TaskType.REASONING: [
                "anthropic",
                "openai",
            ],
            TaskType.EMBEDDING: [
                "ollama",
                "openai",
            ],
        }

    # ---------------------------------------------------------
    # Main Routing
    # ---------------------------------------------------------

    async def route(
        self,
        request: RouteRequest,
    ) -> BaseLLMProvider:
        """
        Select the best provider.
        """

        # Explicit provider requested
        if request.preferred_provider:

            provider = self.registry.get(
                request.preferred_provider
            )

            if await provider.health_check():
                return provider

        # Explicit model requested
        if request.model:

            try:
                return await self.registry.provider_for_model(
                    request.model
                )

            except Exception:
                logger.exception(
                    "Model lookup failed."
                )

        # Task-based routing
        provider = await self._route_by_task(
            request.task
        )

        if provider:
            return provider

        raise NoAvailableProviderError(
            "No healthy provider available."
        )

    # ---------------------------------------------------------
    # Task Routing
    # ---------------------------------------------------------

    async def _route_by_task(
        self,
        task: TaskType,
    ) -> BaseLLMProvider | None:

        candidates = self._task_preferences.get(
            task,
            [],
        )

        for provider_name in candidates:

            try:

                provider = self.registry.get(
                    provider_name
                )

                if await provider.health_check():
                    return provider

            except Exception:
                logger.exception(
                    "Provider %s unavailable.",
                    provider_name,
                )

        return None

    # ---------------------------------------------------------
    # Failover
    # ---------------------------------------------------------

    async def fallback(
        self,
        failed_provider: str,
    ) -> BaseLLMProvider:

        healthy = await self.registry.healthy_providers()

        healthy = [
            p
            for p in healthy
            if p != failed_provider.lower()
        ]

        if not healthy:
            raise RoutingError(
                "No fallback provider available."
            )

        return self.registry.get(
            healthy[0]
        )

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------

    async def healthy_providers(
        self,
    ) -> list[str]:

        return await self.registry.healthy_providers()

    async def supports_model(
        self,
        provider: str,
        model: str,
    ) -> bool:

        return await self.registry.supports_model(
            provider,
            model,
        )