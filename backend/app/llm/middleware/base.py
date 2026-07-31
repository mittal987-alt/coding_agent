from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.llm.provider import (
    ChatRequest,
    ChatResponse,
)


class BaseMiddleware(ABC):
    """
    Base middleware interface.
    """

    @abstractmethod
    async def before_request(
        self,
        request: ChatRequest,
    ) -> ChatRequest:
        """
        Executed before provider call.
        """

    @abstractmethod
    async def after_response(
        self,
        request: ChatRequest,
        response: ChatResponse,
    ) -> ChatResponse:
        """
        Executed after provider returns.
        """

    @abstractmethod
    async def on_error(
        self,
        request: ChatRequest,
        error: Exception,
    ) -> None:
        """
        Executed when provider raises.
        """ 