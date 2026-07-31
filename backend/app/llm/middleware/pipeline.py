from __future__ import annotations

from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)

from .base import BaseMiddleware


class MiddlewarePipeline:
    """
    Executes middleware chain.
    """

    def __init__(
        self,
        middleware: list[BaseMiddleware] | None = None,
    ) -> None:

        self.middleware = middleware or []

    def add(
        self,
        middleware: BaseMiddleware,
    ) -> None:

        self.middleware.append(
            middleware
        )

    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:

        current = request

        for mw in self.middleware:
            current = await mw.before_request(
                current
            )

        return current

    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:

        current = response

        for mw in reversed(self.middleware):
            current = await mw.after_response(
                request,
                current,
            )

        return current

    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:

        for mw in reversed(self.middleware):
            await mw.on_error(
                request,
                error,
            )