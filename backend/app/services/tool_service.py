from __future__ import annotations

from typing import Any

from app.config.settings import Settings
from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ToolExecutionError,
    ValidationError,
)
from app.services.base import BaseService
class ToolService(BaseService):
    """
    Manages tool registration, execution,
    permissions, and sandbox integration.
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
    def registry(self):
        return self.resolve("tool_registry")


    @property
    def sandbox(self):
        return self.resolve("sandbox")


    @property
    def mcp(self):
        return self.resolve("mcp_manager")
    async def list(self):

        return await self.registry.list()
    async def get(
        self,
        tool_name: str,
    ):

        tool = await self.registry.get(
            tool_name,
        )

        if tool is None:
            raise NotFoundError(
                "Tool not found."
            )

        return tool
    async def register(
        self,
        tool,
    ):

        await self.registry.register(
            tool,
        )

        await self.publish(
            "tool.registered",
            {
                "tool": tool.name,
            },
        )

        return tool
    async def unregister(
        self,
        tool_name: str,
    ):

        await self.registry.unregister(
            tool_name,
        )

        await self.publish(
            "tool.unregistered",
            {
                "tool": tool_name,
            },
        )

        return True
    async def execute(
        self,
        *,
        tool_name: str,
        arguments: dict,
        workspace: str | None = None,
        user_id: str | None = None,
    ):

        tool = await self.get(
            tool_name,
        )

        if tool.requires_workspace and workspace is None:
            raise ValidationError(
                "Workspace required."
            )

        if not await tool.authorize(user_id):
            raise PermissionDeniedError(
                "Permission denied."
            )

        try:

            result = await tool.execute(
                arguments=arguments,
                workspace=workspace,
            )

            await self.publish(
                "tool.executed",
                {
                    "tool": tool_name,
                },
            )

            return result

        except Exception as exc:

            raise ToolExecutionError(
                str(exc),
            ) from exc
    async def execute_in_sandbox(
        self,
        *,
        command: str,
        workspace: str,
    ):

        return await self.sandbox.execute(

            command=command,

            workspace=workspace,
        )
    async def discover_mcp_tools(self):

        return await self.mcp.discover()
    async def execute_mcp(
        self,
        *,
        server: str,
        tool: str,
        arguments: dict,
    ):

        return await self.mcp.execute(

            server=server,

            tool=tool,

            arguments=arguments,
        )
    async def validate(
        self,
        tool_name: str,
        arguments: dict,
    ):

        tool = await self.get(
            tool_name,
        )

        return tool.validate(
            arguments,
        )
    async def metadata(
        self,
        tool_name: str,
    ):

        tool = await self.get(
            tool_name,
        )

        return tool.metadata()
    async def statistics(self):

        return await self.registry.statistics()
    async def health_check(self):

        return {
            "service": "ToolService",
            "healthy": True,
            "registry": True,
            "sandbox": True,
            "mcp": True,
        }