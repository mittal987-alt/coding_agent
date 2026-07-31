from __future__ import annotations

import asyncio
from typing import Any

from app.config.settings import Settings
from app.services.base import BaseServiceclass HealthService(BaseService):
    """
    Aggregates health information from
    all application components.
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

    @property
    def database(self):
        return self.resolve("database")


    @property
    def cache(self):
        return self.resolve("cache")


    @property
    def vector_store(self):
        return self.resolve("vector_store")


    @property
    def llm(self):
        return self.resolve("llm_manager")


    @property
    def workspace(self):
        return self.resolve("workspace_manager")


    @property
    def sandbox(self):
        return self.resolve("sandbox")


    @property
    def mcp(self):
        return self.resolve("mcp_manager")


    @property
    def event_bus(self):
        return self.resolve("event_bus")                   

    async def database_health(self):

        try:

            await self.database.ping()

            return {
                "status": "healthy",
            }

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def cache_health(self):

        try:

            await self.cache.ping()

            return {
                "status": "healthy",
            }

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def vector_store_health(self):

        try:

            await self.vector_store.health()

            return {
                "status": "healthy",
            }

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def llm_health(self):

        try:

            return await self.llm.health()

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def workspace_health(self):

        try:

            return await self.workspace.health()

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def sandbox_health(self):

        try:

            return await self.sandbox.health()

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def mcp_health(self):

        try:

            return await self.mcp.health()

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def event_bus_health(self):

        try:

            return await self.event_bus.health()

        except Exception as exc:

            return {
                "status": "unhealthy",
                "error": str(exc),
            }
    async def health(self):

        checks = await asyncio.gather(

            self.database_health(),

            self.cache_health(),

            self.vector_store_health(),

            self.llm_health(),

            self.workspace_health(),

            self.sandbox_health(),

            self.mcp_health(),

            self.event_bus_health(),
        )

        names = [
            "database",
            "cache",
            "vector_store",
            "llm",
            "workspace",
            "sandbox",
            "mcp",
            "event_bus",
        ]

        components = dict(zip(names, checks))

        overall = "healthy"

        for component in components.values():

            if component["status"] != "healthy":

                overall = "degraded"

                break

        return {
            "status": overall,
            "components": components,
        }
    async def live(self):

        return {
            "status": "alive",
        }
    async def ready(self):

        report = await self.health()

        return {
            "ready": report["status"] == "healthy",
            "status": report["status"],
        }
    async def metrics(self):

        return {
            "uptime": await self.resolve("metrics").uptime(),
            "requests": await self.resolve("metrics").requests(),
            "tokens": await self.resolve("metrics").tokens(),
            "cost": await self.resolve("metrics").cost(),
        }   
    async def version(self):

        return {
            "application": self.settings.APP_NAME,
            "version": self.settings.APP_VERSION,
            "environment": self.settings.ENVIRONMENT,
        }
    async def health_check(self):

        return await self.health()