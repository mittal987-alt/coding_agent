from __future__ import annotations

import contextvars
import time
import uuid
from dataclasses import dataclass

from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)

from .base import BaseMiddleware


# ============================================================
# Context
# ============================================================

_current_trace: contextvars.ContextVar[str | None] = (
    contextvars.ContextVar(
        "trace_id",
        default=None,
    )
)

_current_span: contextvars.ContextVar[str | None] = (
    contextvars.ContextVar(
        "span_id",
        default=None,
    )
)


# ============================================================
# Models
# ============================================================


@dataclass(slots=True)
class TraceContext:
    trace_id: str
    span_id: str
    parent_span: str | None = None


# ============================================================
# Middleware
# ============================================================


class TracingMiddleware(BaseMiddleware):
    """
    Provides request tracing.

    Future:
    - OpenTelemetry
    - Jaeger
    - Zipkin
    - Datadog
    """

    def __init__(self) -> None:

        self._start_times: dict[int, float] = {}

        self._contexts: dict[int, TraceContext] = {}

    # ---------------------------------------------------------

    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:

        trace_id = (
            _current_trace.get()
            or uuid.uuid4().hex
        )

        parent = _current_span.get()

        span_id = uuid.uuid4().hex

        context = TraceContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span=parent,
        )

        _current_trace.set(trace_id)

        _current_span.set(span_id)

        self._contexts[id(request)] = context

        self._start_times[id(request)] = (
            time.perf_counter()
        )

        return request

    # ---------------------------------------------------------

    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:

        self._cleanup(request)

        return response

    # ---------------------------------------------------------

    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:

        self._cleanup(request)

    # ---------------------------------------------------------

    def trace_context(
        self,
        request: ChatRequest,
    ) -> TraceContext | None:

        return self._contexts.get(
            id(request)
        )

    # ---------------------------------------------------------

    def current_trace_id(
        self,
    ) -> str | None:

        return _current_trace.get()

    # ---------------------------------------------------------

    def current_span_id(
        self,
    ) -> str | None:

        return _current_span.get()

    # ---------------------------------------------------------

    def _cleanup(
        self,
        request: ChatRequest,
    ) -> None:

        self._contexts.pop(
            id(request),
            None,
        )

        self._start_times.pop(
            id(request),
            None,
        )