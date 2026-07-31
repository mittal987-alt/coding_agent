from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable

logger = logging.getLogger(__name__)

EventHandler = Callable[[Any], Awaitable[None] | None]


@dataclass(slots=True)
class Event:
    """
    Base event.
    """

    name: str

    payload: dict[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(default_factory=datetime.utcnow)

    correlation_id: str | None = None

    execution_id: str | None = None


class EventBus:
    """
    Asynchronous Pub/Sub Event Bus.

    Every module communicates through this class.
    """

    def __init__(self) -> None:

        self._subscribers: dict[
            str,
            list[EventHandler],
        ] = defaultdict(list)

    def subscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:
        """
        Register an event handler.
        """

        logger.info(
            "Subscribed %s -> %s",
            event_name,
            handler.__name__,
        )

        self._subscribers[event_name].append(
            handler
        )

    def unsubscribe(
        self,
        event_name: str,
        handler: EventHandler,
    ) -> None:

        if handler in self._subscribers[event_name]:

            self._subscribers[event_name].remove(
                handler
            )

    async def publish(
        self,
        event: Event,
    ) -> None:
        """
        Publish an event.

        All handlers execute concurrently.
        """

        handlers = self._subscribers.get(
            event.name,
            [],
        )

        if not handlers:

            logger.debug(
                "No subscribers for event %s",
                event.name,
            )

            return

        logger.info(
            "Publishing %s to %d handlers",
            event.name,
            len(handlers),
        )

        tasks = []

        for handler in handlers:

            if inspect.iscoroutinefunction(
                handler
            ):

                tasks.append(handler(event))

            else:

                async def wrapper(
                    h=handler,
                ):
                    h(event)

                tasks.append(wrapper())

        results = await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        for result in results:

            if isinstance(
                result,
                Exception,
            ):

                logger.exception(
                    "Event handler failed",
                    exc_info=result,
                )

    async def publish_name(
        self,
        name: str,
        **payload: Any,
    ) -> None:
        """
        Convenience helper.
        """

        await self.publish(
            Event(
                name=name,
                payload=payload,
            )
        )

    def subscribers(
        self,
        event_name: str,
    ) -> list[EventHandler]:

        return list(
            self._subscribers.get(
                event_name,
                [],
            )
        )

    def clear(self) -> None:
        """
        Remove all subscribers.
        """

        self._subscribers.clear()


event_bus = EventBus()