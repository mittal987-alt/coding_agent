from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from app.bootstrap.container import ServiceContainer

logger = logging.getLogger(__name__)

LifecycleHook = Callable[[ServiceContainer], Awaitable[None]]


class ApplicationLifecycle:
    """
    Manages the lifecycle of the application.

    Responsibilities:
    - Startup
    - Shutdown
    - Startup hooks
    - Shutdown hooks
    """

    def __init__(
        self,
        container: ServiceContainer,
    ) -> None:

        self.container = container
        self._startup_hooks: list[LifecycleHook] = []
        self._shutdown_hooks: list[LifecycleHook] = []
        self._started = False
        self._stopped = False

    def add_startup_hook(self, hook: LifecycleHook) -> None:
        self._startup_hooks.append(hook)

    def add_shutdown_hook(self, hook: LifecycleHook) -> None:
        self._shutdown_hooks.append(hook)

    async def startup(self) -> None:

        if self._started:
            return

        logger.info("Starting application...")

        for hook in self._startup_hooks:
            logger.info("Running startup hook: %s", hook.__name__)
            await hook(self.container)

        self._started = True
        logger.info("Application started.")

    async def shutdown(self) -> None:

        if self._stopped:
            return

        logger.info("Stopping application...")

        for hook in reversed(self._shutdown_hooks):
            try:
                logger.info("Running shutdown hook: %s", hook.__name__)
                await hook(self.container)
            except Exception:
                logger.exception("Shutdown hook failed.")

        if self.container.exists("llm_registry"):
            registry = self.container.resolve("llm_registry")
            if hasattr(registry, "shutdown"):
                await registry.shutdown()

        self._stopped = True
        logger.info("Application stopped.")

    async def restart(self) -> None:
        await self.shutdown()
        self._started = False
        self._stopped = False
        await self.startup()


# ----------------------------------------------------------------
# Lifecycle hook implementations
# ----------------------------------------------------------------

def _get_service(container, name: str):
    """Helper to resolve services from both container types."""
    if hasattr(container, "resolve"):
        return container.resolve(name) if container.exists(name) else None
    return getattr(container, name, None)


async def initialize_memory(container) -> None:
    memory = _get_service(container, "memory")
    if memory and hasattr(memory, "initialize"):
        await memory.initialize()


async def initialize_workspace(container) -> None:
    workspace = _get_service(container, "workspace")
    if workspace and hasattr(workspace, "initialize"):
        await workspace.initialize()


async def initialize_tool_registry(container) -> None:
    registry = _get_service(container, "tool_registry")
    if registry and hasattr(registry, "initialize"):
        await registry.initialize()


async def close_memory(container) -> None:
    memory = _get_service(container, "memory")
    if memory and hasattr(memory, "close"):
        await memory.close()


async def close_workspace(container) -> None:
    workspace = _get_service(container, "workspace")
    if workspace and hasattr(workspace, "close"):
        await workspace.close()


async def close_tool_registry(container) -> None:
    registry = _get_service(container, "tool_registry")
    if registry and hasattr(registry, "close"):
        await registry.close()


# ----------------------------------------------------------------
# Simple on_startup / on_shutdown for ApplicationContainer pattern
# ----------------------------------------------------------------

async def on_startup() -> None:
    from app.bootstrap.container import container as app_container
    logger.info("Starting up application components...")
    await initialize_memory(app_container)  # type: ignore[arg-type]
    await initialize_workspace(app_container)  # type: ignore[arg-type]
    await initialize_tool_registry(app_container)  # type: ignore[arg-type]
    logger.info("Application components initialized.")


async def on_shutdown() -> None:
    from app.bootstrap.container import container as app_container
    logger.info("Shutting down application components...")
    await close_tool_registry(app_container)  # type: ignore[arg-type]
    await close_workspace(app_container)  # type: ignore[arg-type]
    await close_memory(app_container)  # type: ignore[arg-type]
    logger.info("Application components shut down.")