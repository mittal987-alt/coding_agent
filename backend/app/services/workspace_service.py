from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config.settings import Settings
from app.core.exceptions import (
    ConflictError,
    NotFoundError,
)
from app.services.base import BaseService
class WorkspaceService(BaseService):
    """
    Manages workspaces, repositories,
    filesystem operations and Git.
    """

    def __init__(
        self,
        *,
        settings: Settings,
        container: Any,
    ):

        super().__init__(
            settings=settings,
            container=container,
        )
    @property
    def manager(self):
        return self.resolve("workspace_manager")


    @property
    def git(self):
        return self.resolve("git_manager")


    @property
    def filesystem(self):
        return self.resolve("filesystem")
    async def create(
        self,
        *,
        name: str,
        description: str | None = None,
        template: str | None = None,
    ):

        workspace = await self.manager.create(

            name=name,

            description=description,

            template=template,
        )

        await self.publish(

            "workspace.created",

            {
                "workspace": workspace.id,
            },
        )

        return workspace
    async def list(self):

        return await self.manager.list()

    async def get(
        self,
        workspace_id: str,
    ):

        workspace = await self.manager.get(
            workspace_id,
        )

        if workspace is None:
            raise NotFoundError(
                "Workspace not found."
            )

        return workspace
    async def delete(
        self,
        workspace_id: str,
    ):

        await self.manager.delete(
            workspace_id,
        )

        await self.publish(

            "workspace.deleted",

            {
                "workspace": workspace_id,
            },
        )

        return True
    async def clone(
        self,
        *,
        workspace_id: str,
        repository: str,
        branch: str = "main",
    ):

        return await self.git.clone(

            workspace_id=workspace_id,

            repository=repository,

            branch=branch,
        )
    async def read_file(
        self,
        workspace_id: str,
        path: str,
    ):

        return await self.manager.read_file(

            workspace_id,

            path,
        )
    async def write_file(
        self,
        workspace_id: str,
        path: str,
        content: str,
    ):

        return await self.manager.write_file(

            workspace_id,

            path,

            content,
        )
    async def delete_file(
        self,
        workspace_id: str,
        path: str,
    ):

        return await self.manager.delete_file(

            workspace_id,

            path,
        )
    async def list_directory(
        self,
        workspace_id: str,
        path: str = ".",
    ):

        return await self.manager.list_directory(

            workspace_id,

            path,
        )
    async def terminal(
        self,
        *,
        workspace_id: str,
        command: str,
    ):

        return await self.manager.execute_terminal(

            workspace_id,

            command,
        )
    async def git_status(
        self,
        workspace_id: str,
    ):

        return await self.git.status(
            workspace_id,
        )
    async def git_commit(
        self,
        *,
        workspace_id: str,
        message: str,
    ):

        return await self.git.commit(

            workspace_id,

            message,
        )
    async def git_push(
        self,
        *,
        workspace_id: str,
        remote: str = "origin",
        branch: str = "main",
    ):

        return await self.git.push(

            workspace_id,

            remote,

            branch,
        )
    async def git_pull(
        self,
        *,
        workspace_id: str,
        remote: str = "origin",
        branch: str = "main",
    ):

        return await self.git.pull(

            workspace_id,

            remote,

            branch,
        )
    async def statistics(
        self,
        workspace_id: str,
    ):

        return await self.manager.statistics(
            workspace_id,
        )
    async def health(
        self,
        workspace_id: str,
    ):

        return await self.manager.health(
            workspace_id,
        )
    async def archive(
        self,
        workspace_id: str,
    ):

        return await self.manager.archive(
            workspace_id,
        )
    async def restore(
        self,
        workspace_id: str,
    ):

        return await self.manager.restore(
            workspace_id,
        )
    async def health_check(self):

        return {

            "service": "WorkspaceService",

            "healthy": True,

            "workspace_manager": True,

            "git": True,

            "filesystem": True,
        }