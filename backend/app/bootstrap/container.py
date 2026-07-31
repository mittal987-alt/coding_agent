from __future__ import annotations
from app.coding.config import (
    settings,
    llm_config,
    memory_config,
    tools_config,
    workspace_config,
    logging_config,
)


from typing import Any

from app.llm.registry import LLMRegistry
from app.llm.router import LLMRouter
from app.llm.prompts import PromptRegistry, PromptBuilder
from app.tools.registry import ToolRegistry

class ApplicationContainer:
    def __init__(self):
        # Configuration
        self.settings = settings
        self.llm_config = llm_config
        self.memory_config = memory_config
        self.tools_config = tools_config
        self.workspace_config = workspace_config
        self.logging_config = logging_config

        # Services
        self.llm_registry = LLMRegistry()
        self.llm_router = LLMRouter(registry=self.llm_registry)
        
        self.prompt_registry = PromptRegistry()
        self.prompt_builder = PromptBuilder(registry=self.prompt_registry)
        
        self.tool_registry = ToolRegistry()
        
        # Placeholders for initialization in providers
        self.llm_manager = None

container = ApplicationContainer()


class ServiceContainer:
    """
    Dependency Injection Container.

    Every singleton service used by the application
    is registered here.

    Example:

        container.register("llm", llm_manager)

        llm = container.resolve("llm")
    """

    def __init__(self) -> None:

        self._services: dict[str, Any] = {}

        self._factories: dict[str, Any] = {}

        self._singletons: dict[str, Any] = {}

    # ---------------------------------------------------------
    # Register Existing Instance
    # ---------------------------------------------------------

    def register(
        self,
        name: str,
        service: Any,
    ) -> None:

        if name in self._services:

            raise ValueError(
                f"Service '{name}' already registered."
            )

        self._services[name] = service

    # ---------------------------------------------------------
    # Register Lazy Factory
    # ---------------------------------------------------------

    def register_factory(
        self,
        name: str,
        factory,
        *,
        singleton: bool = True,
    ) -> None:

        self._factories[name] = (
            factory,
            singleton,
        )

    # ---------------------------------------------------------
    # Resolve Service
    # ---------------------------------------------------------

    def resolve(
        self,
        name: str,
    ) -> Any:

        if name in self._services:

            return self._services[name]

        if name not in self._factories:

            raise KeyError(
                f"Unknown service '{name}'."
            )

        factory, singleton = self._factories[name]

        if singleton:

            if name not in self._singletons:

                self._singletons[name] = factory(
                    self,
                )

            return self._singletons[name]

        return factory(self)

    # ---------------------------------------------------------
    # Exists
    # ---------------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:

        return (
            name in self._services
            or name in self._factories
        )

    # ---------------------------------------------------------
    # Remove
    # ---------------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:

        self._services.pop(name, None)

        self._factories.pop(name, None)

        self._singletons.pop(name, None)

    # ---------------------------------------------------------
    # Clear
    # ---------------------------------------------------------

    def clear(self) -> None:

        self._services.clear()

        self._factories.clear()

        self._singletons.clear()

    # ---------------------------------------------------------
    # List
    # ---------------------------------------------------------

    def services(
        self,
    ) -> list[str]:

        names = set()

        names.update(self._services)

        names.update(self._factories)

        return sorted(names)

    # ---------------------------------------------------------
    # Python Helpers
    # ---------------------------------------------------------

    def __contains__(
        self,
        item: str,
    ) -> bool:

        return self.exists(item)

    def __getitem__(
        self,
        item: str,
    ) -> Any:

        return self.resolve(item)

    def __setitem__(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.register(key, value)

    def __repr__(
        self,
    ) -> str:

        return (
            f"ServiceContainer("
            f"services={len(self.services())})"
        )