from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.bootstrap.container import ServiceContainer
from app.bootstrap.health import HealthManager
from app.bootstrap.lifecycle import ApplicationLifecycle

logger = logging.getLogger(__name__)


class Application:
    """
    Root application object.

    Owns the dependency container, lifecycle,
    health manager and FastAPI instance.
    """

    def __init__(
        self,
        *,
        container: ServiceContainer,
        lifecycle: ApplicationLifecycle,
        health: HealthManager,
    ) -> None:

        self.container = container
        self.lifecycle = lifecycle
        self.health = health

        self.fastapi = FastAPI(
            title="AI Software Engineer",
            version="1.0.0",
            lifespan=self._lifespan,
        )

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):

        logger.info("Application startup...")

        await self.lifecycle.startup()

        yield

        logger.info("Application shutdown...")

        await self.lifecycle.shutdown()

    def resolve(self, service: str) -> Any:
        return self.container.resolve(service)

    def register(self, name: str, service: Any) -> None:
        self.container.register(name, service)

    async def health_report(self):
        return await self.health.json()

    @property
    def app(self) -> FastAPI:
        return self.fastapi

    def include_router(
        self,
        router,
        *,
        prefix: str = "",
        tags: list[str] | None = None,
    ) -> None:
        self.fastapi.include_router(router, prefix=prefix, tags=tags)

    def add_middleware(self, middleware, **kwargs) -> None:
        self.fastapi.add_middleware(middleware, **kwargs)

    def add_event_handler(self, event: str, handler) -> None:
        self.fastapi.add_event_handler(event, handler)

    @property
    def state(self):
        return self.fastapi.state

    def __getitem__(self, name: str):
        return self.container.resolve(name)

    def __repr__(self) -> str:
        return f"Application(services={len(self.container.services())})"