# LLM Streaming
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Any

from .exceptions import StreamingError
from .provider import (
    ChatResponse,
    StreamChunk,
)
from .response import StreamResponseBuilder


# ============================================================
# Callback Types
# ============================================================

StreamCallback = Callable[
    [StreamChunk],
    Awaitable[None],
]

CompletionCallback = Callable[
    [ChatResponse],
    Awaitable[None],
]


# ============================================================
# Event Handler
# ============================================================


class StreamEventHandler:
    """
    Handles streaming events.
    """

    def __init__(self) -> None:

        self._chunk_callbacks: list[
            StreamCallback
        ] = []

        self._completion_callbacks: list[
            CompletionCallback
        ] = []

    def on_chunk(
        self,
        callback: StreamCallback,
    ) -> None:

        self._chunk_callbacks.append(callback)

    def on_complete(
        self,
        callback: CompletionCallback,
    ) -> None:

        self._completion_callbacks.append(callback)

    async def emit_chunk(
        self,
        chunk: StreamChunk,
    ) -> None:

        for callback in self._chunk_callbacks:
            await callback(chunk)

    async def emit_completion(
        self,
        response: ChatResponse,
    ) -> None:

        for callback in self._completion_callbacks:
            await callback(response)


# ============================================================
# Stream Controller
# ============================================================


class StreamController:
    """
    Coordinates provider streaming.
    """

    def __init__(
        self,
        *,
        model: str,
        handler: StreamEventHandler | None = None,
    ) -> None:

        self.model = model

        self.handler = handler or StreamEventHandler()

        self.builder = StreamResponseBuilder()

        self._cancelled = False

        self._finished = False

    @property
    def cancelled(
        self,
    ) -> bool:
        return self._cancelled

    @property
    def finished(
        self,
    ) -> bool:
        return self._finished

    async def consume(
        self,
        stream: AsyncIterator[StreamChunk],
    ) -> ChatResponse:
        """
        Consume provider stream.
        """

        try:

            async for chunk in stream:

                if self._cancelled:
                    break

                self.builder.add_chunk(chunk)

                await self.handler.emit_chunk(chunk)

            response = self.builder.build(
                model=self.model,
            )

            self._finished = True

            await self.handler.emit_completion(
                response
            )

            return response

        except Exception as exc:
            raise StreamingError(
                str(exc)
            ) from exc

    def cancel(
        self,
    ) -> None:

        self._cancelled = True


# ============================================================
# Streaming Provider Interface
# ============================================================


class BaseStreamingProvider(ABC):
    """
    Optional interface for providers
    supporting native streaming.
    """

    @abstractmethod
    async def stream(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        ...


# ============================================================
# Broadcast Manager
# ============================================================


class StreamBroadcaster:
    """
    Broadcast stream chunks to multiple consumers.

    Example:
    - WebSocket
    - CLI
    - Logger
    """

    def __init__(self) -> None:

        self._queues: list[
            asyncio.Queue[StreamChunk]
        ] = []

    def subscribe(
        self,
    ) -> asyncio.Queue[StreamChunk]:

        queue: asyncio.Queue[
            StreamChunk
        ] = asyncio.Queue()

        self._queues.append(queue)

        return queue

    def unsubscribe(
        self,
        queue: asyncio.Queue[StreamChunk],
    ) -> None:

        if queue in self._queues:
            self._queues.remove(queue)

    async def publish(
        self,
        chunk: StreamChunk,
    ) -> None:

        for queue in self._queues:
            await queue.put(chunk)

    async def close(
        self,
    ) -> None:

        for queue in self._queues:
            await queue.put(
                StreamChunk(
                    content="",
                )
            )