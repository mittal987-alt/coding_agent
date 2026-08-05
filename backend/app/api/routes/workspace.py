#
from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import WorkspaceDep
from app.api.schemas.workspace import (
    WorkspaceCreateRequest,
    WorkspaceResponse,
    FileWriteRequest,
    GitCloneRequest,
)

router = APIRouter()

@router.post(
    "/",
    response_model=WorkspaceResponse,
)
async def create_workspace(
    request: WorkspaceCreateRequest,
    workspace: WorkspaceDep,
):

    ws = await workspace.create(

        name=request.name,

        language=request.language,

        template=request.template,
    )

    return WorkspaceResponse.model_validate(ws)

@router.get("/")
async def list_workspaces(
    workspace: WorkspaceDep,
):

    return await workspace.list()

@router.delete("/{workspace_id}")
async def delete_workspace(
    workspace_id: str,
    workspace: WorkspaceDep,
):

    await workspace.delete(
        workspace_id,
    )

    return {
        "success": True,
    }


@router.post("/{workspace_id}/clone")
async def clone_repository(
    workspace_id: str,
    request: GitCloneRequest,
    workspace: WorkspaceDep,
):

    repo = await workspace.clone(
        workspace_id=workspace_id,
        repository=request.repository,
        branch=request.branch,
    )

    return repo
@router.get("/{workspace_id}/file")
async def read_file(
    workspace_id: str,
    path: str,
    workspace: WorkspaceDep,
):

    return {

        "content": await workspace.read_file(

            workspace_id,

            path,
        )
    }

@router.post("/{workspace_id}/file")
async def write_file(
    workspace_id: str,
    request: FileWriteRequest,
    workspace: WorkspaceDep,
):

    await workspace.write_file(

        workspace_id,

        request.path,

        request.content,
    )

    return {
        "success": True,
    }
@router.delete("/{workspace_id}/file")
async def delete_file(
    workspace_id: str,
    path: str,
    workspace: WorkspaceDep,
):

    await workspace.delete_file(

        workspace_id,

        path,
    )

    return {
        "success": True,
    }
@router.get("/{workspace_id}/files")
async def files(
    workspace_id: str,
    workspace: WorkspaceDep,
):

    return await workspace.list_directory(
        workspace_id,
    )
@router.post("/{workspace_id}/terminal")
async def terminal(
    workspace_id: str,
    command: str,
    workspace: WorkspaceDep,
):

    result = await workspace.terminal(
        workspace_id=workspace_id,
        command=command,
    )

    return result
@router.get("/{workspace_id}/git/status")
async def git_status(
    workspace_id: str,
    workspace: WorkspaceDep,
):

    return await workspace.git_status(
        workspace_id,
    )


@router.post("/{workspace_id}/git/commit")
async def git_commit(
    workspace_id: str,
    message: str,
    workspace: WorkspaceDep,
):

    return await workspace.commit(

        workspace_id,

        message,
    )
@router.post("/{workspace_id}/git/push")
async def git_push(
    workspace_id: str,
    workspace: WorkspaceDep,
):

    return await workspace.push(
        workspace_id,
    )