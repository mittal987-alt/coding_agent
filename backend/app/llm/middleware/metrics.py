# Metrics Middleware
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field

from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)

from .base import BaseMiddleware


# ============================================================
# Metrics Models
# ============================================================


@dataclass(slots=True)
class ProviderMetrics:
    """
    Statistics for a single provider/model.
    """

    requests: int = 0

    successes: int = 0

    failures: int = 0

    total_latency_ms: float = 0.0

    total_prompt_tokens: int = 0

    total_completion_tokens: int = 0

    total_tokens: int = 0

    estimated_cost: float = 0.0


@dataclass(slots=True)
class MetricsSnapshot:
    providers: dict[str, ProviderMetrics] = field(
        default_factory=dict
    )


# ============================================================
# Metrics Middleware
# ============================================================


class MetricsMiddleware(BaseMiddleware):
    """
    Collects provider statistics.
    """

    def __init__(self) -> None:

        self._metrics = defaultdict(
            ProviderMetrics
        )

        self._started: dict[int, float] = {}

    # ---------------------------------------------------------

    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:

        key = id(request)

        self._started[key] = (
            time.perf_counter()
        )

        provider = self._metrics[
            request.model
        ]

        provider.requests += 1

        return request

    # ---------------------------------------------------------

    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:

        key = id(request)

        started = self._started.pop(
            key,
            None,
        )

        latency = 0.0

        if started is not None:
            latency = (
                time.perf_counter()
                - started
            ) * 1000

        stats = self._metrics[
            response.model
        ]

        stats.successes += 1

        stats.total_latency_ms += latency

        if response.usage:

            stats.total_prompt_tokens += (
                response.usage.prompt_tokens
            )

            stats.total_completion_tokens += (
                response.usage.completion_tokens
            )

            stats.total_tokens += (
                response.usage.total_tokens
            )

        return response

    # ---------------------------------------------------------

    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:

        self._started.pop(
            id(request),
            None,
        )

        self._metrics[
            request.model
        ].failures += 1

    # ---------------------------------------------------------

    def snapshot(
        self,
    ) -> MetricsSnapshot:

        return MetricsSnapshot(
            providers=dict(
                self._metrics
            )
        )

    # ---------------------------------------------------------

    def reset(
        self,
    ) -> None:

        self._metrics.clear()

        self._started.clear()

    # ---------------------------------------------------------

    def average_latency(
        self,
        model: str,
    ) -> float:

        stats = self._metrics.get(model)

        if (
            not stats
            or stats.successes == 0
        ):
            return 0.0

        return (
            stats.total_latency_ms
            / stats.successes
        )

    # ---------------------------------------------------------

    def success_rate(
        self,
        model: str,
    ) -> float:

        stats = self._metrics.get(model)

        if (
            not stats
            or stats.requests == 0
        ):
            return 0.0

        return (
            stats.successes
            / stats.requests
        )

    # ---------------------------------------------------------

    def provider_metrics(
        self,
        model: str,
    ) -> ProviderMetrics | None:

        return self._metrics.get(model)