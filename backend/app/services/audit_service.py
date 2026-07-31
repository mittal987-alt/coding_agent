from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.config.settings import Settings
from app.services.base import BaseService
class AuditService(BaseService):
    """
    Centralized audit logging service.

    Responsible for:

    - user activity
    - security events
    - tool execution
    - compliance logs
    - searchable audit history
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
    def repository(self):
        return self.resolve("audit_repository")
    async def log(
        self,
        *,
        action: str,
        user: str | None = None,
        resource: str | None = None,
        metadata: dict | None = None,
        status: str = "success",
    ):

        record = {

            "timestamp": datetime.now(
                UTC,
            ),

            "action": action,

            "user": user,

            "resource": resource,

            "status": status,

            "metadata": metadata or {},
        }

        await self.repository.create(
            record,
        )

        return record
    async def login(
        self,
        user: str,
        ip: str,
    ):

        return await self.log(

            action="user.login",

            user=user,

            metadata={
                "ip": ip,
            },
        )
    async def logout(
        self,
        user: str,
    ):

        return await self.log(

            action="user.logout",

            user=user,
        )
    async def failed_login(
        self,
        email: str,
        ip: str,
    ):

        return await self.log(

            action="login.failed",

            metadata={
                "email": email,
                "ip": ip,
            },

            status="failed",
        )
    async def failed_login(
        self,
        email: str,
        ip: str,
    ):

        return await self.log(

            action="login.failed",

            metadata={
                "email": email,
                "ip": ip,
            },

            status="failed",
        )
    async def tool_execution(
        self,
        *,
        tool: str,
        user: str | None,
        duration: float,
    ):

        return await self.log(

            action="tool.executed",

            user=user,

            metadata={
                "tool": tool,
                "duration": duration,
            },
        )
    async def agent_execution(
        self,
        *,
        task_id: str,
        user: str | None,
        goal: str,
    ):

        return await self.log(

            action="agent.executed",

            user=user,

            resource=task_id,

            metadata={
                "goal": goal,
            },
        )   
    async def security_event(
        self,
        *,
        event: str,
        metadata: dict,
    ):

        return await self.log(

            action="security",

            metadata={
                "event": event,
                **metadata,
            },
        )
    async def search(
        self,
        *,
        user: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ):

        return await self.repository.search(

            user=user,

            action=action,

            limit=limit,
        )
    async def recent(
        self,
        limit: int = 50,
    ):

        return await self.repository.recent(
            limit,
        )
    async def cleanup(
        self,
        days: int,
    ):

        return await self.repository.cleanup(
            days,
        )
    async def export(
        self,
        *,
        start,
        end,
    ):

        return await self.repository.export(

            start=start,

            end=end,
        )
    async def statistics(self):

        return await self.repository.statistics()
    async def health_check(self):

        return {

            "service": "AuditService",

            "healthy": True,

            "repository": True,
        }