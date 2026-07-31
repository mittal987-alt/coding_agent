# Retry Middleware
from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from app.llm.exceptions import (
    ProviderConnectionError,
    ProviderTimeoutError,
    RateLimitError,
    RetryLimitExceededError,
)


@dataclass(slots=True)
class RetryPolicy:
    """
    Configuration for retry behavior.
    """

    max_retries: int = 3

    initial_delay: float = 1.0

    max_delay: float = 30.0

    exponential_base: float = 2.0

    jitter: bool = True


class RetryMiddleware:
    """
    Retry wrapper with exponential backoff.
    """

    def __init__(
        self,
        policy: RetryPolicy | None = None,
    ) -> None:

        self.policy = policy or RetryPolicy()

        self.retryable = (
            ProviderConnectionError,
            ProviderTimeoutError,
            RateLimitError,
        )

    # ---------------------------------------------------------

    async def execute(
        self,
        operation: Callable[[], Awaitable],
    ):

        last_error = None

        for attempt in range(
            self.policy.max_retries + 1
        ):

            try:
                return await operation()

            except self.retryable as exc:

                last_error = exc

                if attempt >= self.policy.max_retries:
                    break

                delay = self._delay(attempt)

                await asyncio.sleep(delay)

        raise RetryLimitExceededError(
            str(last_error)
        ) from last_error

    # ---------------------------------------------------------

    def _delay(
        self,
        attempt: int,
    ) -> float:

        delay = min(
            self.policy.initial_delay
            * (
                self.policy.exponential_base
                ** attempt
            ),
            self.policy.max_delay,
        )

        if self.policy.jitter:

            delay *= random.uniform(
                0.8,
                1.2,
            )

        return delay