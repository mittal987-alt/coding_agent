from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.bootstrap.container import ServiceContainer, container as app_container
from app.bootstrap.health import HealthManager
from app.bootstrap.lifecycle import (
    ApplicationLifecycle,
    initialize_memory,
    initialize_workspace,
    initialize_tool_registry,
    close_memory,
    close_workspace,
    close_tool_registry,
    on_startup,
    on_shutdown,
)
from app.bootstrap.providers import initialize_providers, register_services

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------
# lifespan — used by the ApplicationContainer (simple) pattern
# ----------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan for the simple ApplicationContainer-based app."""
    initialize_providers(app_container)
    await on_startup()
    yield
    await on_shutdown()


# ----------------------------------------------------------------
# bootstrap_application — full ServiceContainer pattern
# ----------------------------------------------------------------

def bootstrap_application():
    """
    Build the complete application.

    Steps:
        1. Create DI container
        2. Register services
        3. Configure lifecycle
        4. Configure health
        5. Create Application
    """
    # Import here to avoid circular imports at module level
    from app.bootstrap.application import Application

    logger.info("Bootstrapping application...")

    container = ServiceContainer()

    register_services(container)

    lifecycle = build_lifecycle(container)

    health = HealthManager(container)

    application = Application(
        container=container,
        lifecycle=lifecycle,
        health=health,
    )

    register_builtin_services(container, application, lifecycle, health)

    logger.info("Application bootstrapped successfully.")

    return application


def build_lifecycle(container: ServiceContainer) -> ApplicationLifecycle:

    lifecycle = ApplicationLifecycle(container)

    # Startup hooks
    lifecycle.add_startup_hook(initialize_memory)
    lifecycle.add_startup_hook(initialize_workspace)
    lifecycle.add_startup_hook(initialize_tool_registry)

    # Shutdown hooks
    lifecycle.add_shutdown_hook(close_tool_registry)
    lifecycle.add_shutdown_hook(close_workspace)
    lifecycle.add_shutdown_hook(close_memory)

    return lifecycle


def register_builtin_services(
    container: ServiceContainer,
    application,
    lifecycle: ApplicationLifecycle,
    health: HealthManager,
) -> None:

    container.register("application", application)
    container.register("health_manager", health)
    container.register("lifecycle", lifecycle)


def validate_container(container: ServiceContainer) -> None:
    """
    Validate required services exist.
    """
    required = [
        "settings",
        "llm_manager",
        "llm_registry",
        "llm_router",
    ]

    missing = [s for s in required if not container.exists(s)]

    if missing:
        raise RuntimeError("Missing required services: " + ", ".join(missing))