#
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.dependencies import get_container
from app.api.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
)

router = APIRouter()

@router.post(
    "/",
    response_model=ProjectResponse,
)
async def create_project(
    request: ProjectCreateRequest,
    container=Depends(get_container),
):
    project_manager = container.resolve(
        "project_manager",
    )

    project = await project_manager.create(

        name=request.name,

        description=request.description,

        visibility=request.visibility,
    )

    return ProjectResponse.model_validate(
        project
    )

@router.get("/")
async def list_projects(
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.list()

@router.get("/{project_id}")
async def get_project(
    project_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    project = await manager.get(
        project_id,
    )

    if project is None:

        raise HTTPException(

            status_code=404,

            detail="Project not found.",
        )

    return project

@router.put("/{project_id}")
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.update(

        project_id,

        request.model_dump(
            exclude_unset=True,
        ),
    )

@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    await manager.delete(
        project_id,
    )

    return {
        "success": True,
    }

@router.post("/{project_id}/workspaces")
async def create_workspace(
    project_id: str,
    name: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.create_workspace(

        project_id,

        name,
    )

@router.get("/{project_id}/workspaces")
async def workspaces(
    project_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.workspaces(
        project_id,
    )

@router.post("/{project_id}/repository")
async def link_repository(
    project_id: str,
    repository: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.link_repository(

        project_id,

        repository,
    )

@router.get("/{project_id}/members")
async def members(
    project_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.members(
        project_id,
    )
@router.post("/{project_id}/members")
async def add_member(
    project_id: str,
    email: str,
    role: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.add_member(

        project_id,

        email,

        role,
    )
@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: str,
    user_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    await manager.remove_member(

        project_id,

        user_id,
    )

    return {
        "success": True,
    }
@router.get("/{project_id}/settings")
async def settings(
    project_id: str,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.settings(
        project_id,
    )
@router.put("/{project_id}/settings")
async def update_settings(
    project_id: str,
    settings: dict,
    container=Depends(get_container),
):

    manager = container.resolve(
        "project_manager",
    )

    return await manager.update_settings(

        project_id,

        settings,
    )