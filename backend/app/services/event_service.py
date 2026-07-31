from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any, Awaitable, Callable

from app.config.settings import Settings
from app.services.base import BaseService
EventHandler = Callable[[dict], Awaitable[None]]
class EventService(BaseService):
    """
    Event bus orchestration service.

    Responsible for:

    - publish
    - subscribe
    - websocket notifications
    - event persistence
    - background processing
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ) -> None:

        super().__init__(
            settings=settings,
            container=container,
        )

        self._subscriptions: dict[
            str,
            list[EventHandler],
        ] = defaultdict(list)
    @property
    def websocket(self):
        return self.resolve("websocket_manager")


    @property
    def event_store(self):
        return self.resolve("event_store")


    @property
    def audit(self):
        return self.resolve("audit_service")
    async def subscribe(
        self,
        event: str,
        handler: EventHandler,
    ):

        self._subscriptions[event].append(
            handler,
        )
    async def subscribe(
        self,
        event: str,
        handler: EventHandler,
    ):

        self._subscriptions[event].append(
            handler,
        )
    async def subscribe(
        self,
        event: str,
        handler: EventHandler,
    ):

        self._subscriptions[event].append(
            handler,
        )
    async def unsubscribe(
        self,
        event: str,
        handler: EventHandler,
    ):

        if event not in self._subscriptions:
            return

        self._subscriptions[event].remove(
            handler,
        )
    async def publish(
        self,
        event: str,
        payload: dict,
    ):

        await self.event_store.save(

            event=event,

            payload=payload,
        )

        handlers = self._subscriptions.get(
            event,
            [],
        )

        await asyncio.gather(

            *[
                handler(payload)
                for handler in handlers
            ]
        )

        await self.websocket.broadcast(

            event=event,

            payload=payload,
        )
    async def publish_background(
        self,
        event: str,
        payload: dict,
    ):

        asyncio.create_task(

            self.publish(
                event,
                payload,
            )
        )
    async def replay(
        self,
        event: str,
    ):

        events = await self.event_store.load(
            event,
        )

        handlers = self._subscriptions.get(
            event,
            [],
        )

        for item in events:

            await asyncio.gather(

                *[
                    handler(item.payload)
                    for handler in handlers
                ]
            )
    async def history(
        self,
        limit: int = 100,
    ):

        return await self.event_store.history(
            limit,
        )
    async def subscribers(
        self,
        event: str,
    ):

        return len(
            self._subscriptions.get(
                event,
                [],
            )
        )
    async def subscribers(
        self,
        event: str,
    ):

        return len(
            self._subscriptions.get(
                event,
                [],
            )
        )
    async def registered_events(self):

        return list(
            self._subscriptions.keys()
        )
    async def clear(self):

        await self.event_store.clear()

        return True
    async def statistics(self):

        return {

            "events": len(
                await self.history()
            ),

            "registered_events": len(
                self._subscriptions
            ),
        }
    async def shutdown(self):

        self._subscriptions.clear()
    async def health_check(self):

        return {

            "service": "EventService",

            "healthy": True,

            "subscriptions": len(
                self._subscriptions
            ),
        }