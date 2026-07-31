# Rate Limit Middleware
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

from app.llm.exceptions import RateLimitError
from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)

from .base import BaseMiddleware


# ============================================================
# Configuration
# ============================================================


@dataclass(slots=True)
class RateLimitConfig:
    """
    Rate limiting configuration.
    """

    requests_per_minute: int = 60

    burst_size: int = 10

    max_concurrent_requests: int = 5


# ============================================================
# Token Bucket
# ============================================================


class TokenBucket:
    """
    Simple token bucket implementation.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
    ) -> None:

        self.capacity = capacity

        self.tokens = float(capacity)

        self.refill_rate = refill_rate

        self.last_refill = time.monotonic()

        self.lock = asyncio.Lock()

    async def consume(
        self,
        amount: int = 1,
    ) -> bool:

        async with self.lock:

            now = time.monotonic()

            elapsed = now - self.last_refill

            self.tokens = min(
                self.capacity,
                self.tokens + elapsed * self.refill_rate,
            )

            self.last_refill = now

            if self.tokens >= amount:

                self.tokens -= amount

                return True

            return False


            # ============================================================
# Middleware
# ============================================================


class RateLimitMiddleware(BaseMiddleware):
    """
    Provider-independent rate limiter.
    """

    def __init__(
        self,
        config: RateLimitConfig | None = None,
    ) -> None:

        self.config = config or RateLimitConfig()

        self._buckets: dict[
            str,
            TokenBucket,
        ] = {}

        self._semaphores: dict[
            str,
            asyncio.Semaphore,
        ] = {}

    # ---------------------------------------------------------

    def _bucket(
        self,
        key: str,
    ) -> TokenBucket:

        if key not in self._buckets:

            self._buckets[key] = TokenBucket(
                capacity=self.config.burst_size,
                refill_rate=(
                    self.config.requests_per_minute
                    / 60
                ),
            )

        return self._buckets[key]

    # ---------------------------------------------------------

    def _semaphore(
        self,
        key: str,
    ) -> asyncio.Semaphore:

        if key not in self._semaphores:

            self._semaphores[key] = asyncio.Semaphore(
                self.config.max_concurrent_requests
            )

        return self._semaphores[key]

    # ---------------------------------------------------------

    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:

        key = request.model

        bucket = self._bucket(key)

        allowed = await bucket.consume()

        if not allowed:

            raise RateLimitError(
                f"Rate limit exceeded for model '{key}'."
            )

        semaphore = self._semaphore(key)

        await semaphore.acquire()

        return request

    # ---------------------------------------------------------

    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:

        self._semaphore(
            request.model
        ).release()

        return response

    # ---------------------------------------------------------

    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:

        semaphore = self._semaphore(
            request.model
        )

        try:
            semaphore.release()
        except ValueError:
            # Ignore over-release
            pass