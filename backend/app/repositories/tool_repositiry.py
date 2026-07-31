from __future__ import annotations

from typing import Sequence

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tool import Tool
from app.repositories.base import BaseRepository
class ToolRepository(BaseRepository[Tool]):
    """
    Repository responsible for AI tool persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Tool,
        )
    async def get_by_name(
        self,
        name: str,
    ) -> Tool | None:

        stmt = select(Tool).where(
            Tool.name == name
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[Tool]:

        stmt = (

            select(Tool)

            .where(

                or_(

                    Tool.name.ilike(
                        f"%{query}%"
                    ),

                    Tool.description.ilike(
                        f"%{query}%"
                    ),

                    Tool.category.ilike(
                        f"%{query}%"
                    ),
                )
            )

            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def enabled(self):

        stmt = select(Tool).where(
            Tool.enabled.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def disabled(self):

        stmt = select(Tool).where(
            Tool.enabled.is_(False)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def by_category(
        self,
        category: str,
    ):

        stmt = (
            select(Tool)
            .where(
                Tool.category == category
            )
            .order_by(
                Tool.name
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def update_version(
        self,
        tool_id: str,
        version: str,
    ):

        await self.session.execute(

            update(Tool)

            .where(
                Tool.id == tool_id
            )

            .values(
                version=version,
            )
        )

        await self.session.commit()
    async def enable(
        self,
        tool_id: str,
    ):

        await self.session.execute(

            update(Tool)

            .where(
                Tool.id == tool_id
            )

            .values(
                enabled=True,
            )
        )

        await self.session.commit()
    async def disable(
        self,
        tool_id: str,
    ):

        await self.session.execute(

            update(Tool)

            .where(
                Tool.id == tool_id
            )

            .values(
                enabled=False,
            )
        )

        await self.session.commit()
    async def update_health(
        self,
        tool_id: str,
        healthy: bool,
    ):

        await self.session.execute(

            update(Tool)

            .where(
                Tool.id == tool_id
            )

            .values(
                healthy=healthy,
            )
        )

        await self.session.commit()
    async def increment_usage(
        self,
        tool_id: str,
    ):

        tool = await self.get(tool_id)

        if tool is None:
            return

        await self.session.execute(

            update(Tool)

            .where(
                Tool.id == tool_id
            )

            .values(
                usage_count=tool.usage_count + 1,
            )
        )

        await self.session.commit()
    async def update_runtime(
        self,
        tool_id: str,
        runtime: float,
    ):

        await self.session.execute(

            update(Tool)

            .where(
                Tool.id == tool_id
            )

            .values(
                average_runtime=runtime,
            )
        )

        await self.session.commit()
    async def by_permission(
        self,
        permission: str,
    ):

        stmt = (
            select(Tool)
            .where(
                Tool.permission == permission
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()   
    async def statistics(self):

        total = await self.count()

        enabled_stmt = (
            select(func.count())
            .select_from(Tool)
            .where(Tool.enabled.is_(True))
        )

        enabled = (
            await self.session.execute(
                enabled_stmt
            )
        ).scalar_one()

        healthy_stmt = (
            select(func.count())
            .select_from(Tool)
            .where(Tool.healthy.is_(True))
        )

        healthy = (
            await self.session.execute(
                healthy_stmt
            )
        ).scalar_one()

        return {

            "total": total,

            "enabled": enabled,

            "healthy": healthy,
        }