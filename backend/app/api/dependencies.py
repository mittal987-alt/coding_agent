#
from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.bootstrap.application import Application
from app.bootstrap.container import ServiceContainer

def get_application(
    request: Request,
) -> Application:
    """
    Return the root Application instance.
    """

    application = getattr(
        request.app.state,
        "application",
        None,
    )

    if application is None:
        raise RuntimeError(
            "Application has not been initialized."
        )

    return application

def get_container(
    application: Annotated[
        Application,
        Depends(get_application),
    ],
) -> ServiceContainer:
    """
    Return the application's DI container.
    """

    return application.container
def resolve_service(
    container: ServiceContainer,
    name: str,
):

    if not container.exists(name):

        raise HTTPException(

            status_code=500,

            detail=f"Service '{name}' is not registered.",
        )

    return container.resolve(name)
def get_llm_manager(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "llm_manager",
    )

def get_llm_router(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "llm_router",
    )
def get_llm_registry(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "llm_registry",
    )
def get_workspace(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "workspace",
    )
def get_memory(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "memory",
    )
def get_tool_registry(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "tool_registry",
    )
def get_settings(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "settings",
    )
def get_health_manager(
    container: Annotated[
        ServiceContainer,
        Depends(get_container),
    ],
):

    return resolve_service(
        container,
        "health_manager",
    )
def get_agent(
    name: str,
):
    """
    Factory for resolving agents by name.
    """

    def dependency(
        container: Annotated[
            ServiceContainer,
            Depends(get_container),
        ],
    ):

        return resolve_service(
            container,
            name,
        )

    return dependency