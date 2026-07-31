from __future__ import annotations

from abc import ABC
from typing import Any

from app.config.settings import Settings
class BaseService(ABC):
    """
    Base class for all application services.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ) -> None:

        self.settings = settings

        self.container = container
    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve dependency from DI container.
        """

        return self.container.resolve(name)
    @property
    def logger(self):

        return self.resolve("logger")
    @property
    def database(self):

        return self.resolve("database")
    @property
    def cache(self):

        return self.resolve("cache")
    @property
    def events(self):

        return self.resolve("event_bus")
    @property
    def audit(self):

        return self.resolve("audit_service")
    @property
    def metrics(self):

        return self.resolve("metrics") 
    @property
    def health(self):

        return self.resolve("health_manager")
    async def transaction(self):

        return self.database.transaction()
    async def publish(
        self,
        event: str,
        payload: dict,
    ):

        await self.events.publish(
            event,
            payload,
        )
    async def log_action(
        self,
        *,
        action: str,
        user: str | None = None,
        resource: str | None = None,
        metadata: dict | None = None,
    ):

        await self.audit.log(

            action=action,

            user=user,

            resource=resource,

            metadata=metadata or {},
        )
    async def health_check(self):

        return {
            "service": self.__class__.__name__,
            "healthy": True,
        }

    async def startup(self):

        pass


    async def shutdown(self):

        pass