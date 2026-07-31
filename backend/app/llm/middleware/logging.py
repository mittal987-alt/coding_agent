# Logging Middleware
from __future__ import annotations

import logging
import time

from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)

from .base import BaseMiddleware

logger = logging.getLogger("llm")


class LoggingMiddleware(BaseMiddleware):
    """
    Logs every LLM request and response.

    Features:
    - Request metadata
    - Response metadata
    - Latency
    - Token usage
    - Errors
    """

    def __init__(
        self,
        *,
        log_prompts: bool = False,
        log_responses: bool = False,
    ) -> None:

        self.log_prompts = log_prompts
        self.log_responses = log_responses

        self._request_start: dict[int, float] = {}

    # ---------------------------------------------------------

    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:

        request_id = id(request)

        self._request_start[
            request_id
        ] = time.perf_counter()

        logger.info(
            "LLM Request | model=%s temperature=%s stream=%s",
            request.model,
            request.temperature,
            request.stream,
        )

        if self.log_prompts:

            for message in request.messages:

                logger.debug(
                    "[%s] %s",
                    message.role.value,
                    message.content,
                )

        return request

    # ---------------------------------------------------------

    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:

        request_id = id(request)

        started = self._request_start.pop(
            request_id,
            None,
        )

        latency = None

        if started is not None:
            latency = (
                time.perf_counter()
                - started
            ) * 1000

        logger.info(
            (
                "LLM Response | "
                "model=%s "
                "latency=%.2fms "
                "tokens=%s"
            ),
            response.model,
            latency or 0,
            (
                response.usage.total_tokens
                if response.usage
                else "-"
            ),
        )

        if (
            self.log_responses
            and response.message
        ):
            logger.debug(
                "%s",
                response.message.content,
            )

        return response

    # ---------------------------------------------------------

    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:

        request_id = id(request)

        started = self._request_start.pop(
            request_id,
            None,
        )

        latency = None

        if started is not None:
            latency = (
                time.perf_counter()
                - started
            ) * 1000

        logger.exception(
            (
                "LLM Error | "
                "model=%s "
                "latency=%.2fms "
                "error=%s"
            ),
            request.model,
            latency or 0,
            error,
        )