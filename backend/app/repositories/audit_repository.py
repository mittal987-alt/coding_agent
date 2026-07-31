from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository

class AuditRepository(BaseRepository[AuditLog]):
    """
    Repository for audit log persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=AuditLog,
        )



async def by_action(
        self,
        action: str,
    ) -> Sequence[AuditLog]:

        stmt = (
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def by_user(
        self,
        user_id: str,
    ) -> Sequence[AuditLog]:

        stmt = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def search(
        self,
        *,
        user: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ):

        stmt = select(AuditLog)

        filters = []

        if user:
            filters.append(
                AuditLog.user_id == user
            )

        if action:
            filters.append(
                AuditLog.action == action
            )

        if filters:

            stmt = stmt.where(
                and_(*filters)
            )

        stmt = (
            stmt
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def search(
        self,
        *,
        user: str | None = None,
        action: str | None = None,
        limit: int = 100,
    ):

        stmt = select(AuditLog)

        filters = []

        if user:
            filters.append(
                AuditLog.user_id == user
            )

        if action:
            filters.append(
                AuditLog.action == action
            )

        if filters:

            stmt = stmt.where(
                and_(*filters)
            )

        stmt = (
            stmt
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def recent(
        self,
        limit: int = 50,
    ):

        stmt = (
            select(AuditLog)
            .order_by(
                AuditLog.created_at.desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def between(
        self,
        start: datetime,
        end: datetime,
    ):

        stmt = (
            select(AuditLog)
            .where(
                AuditLog.created_at.between(
                    start,
                    end,
                )
            )
            .order_by(
                AuditLog.created_at.desc()
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def cleanup(
        self,
        days: int,
    ):

        cutoff = datetime.now(
            UTC,
        ) - timedelta(days=days)

        stmt = (
            select(AuditLog)
            .where(
                AuditLog.created_at < cutoff
            )
        )

        result = await self.session.execute(stmt)

        logs = result.scalars().all()

        for log in logs:
            await self.session.delete(log)

        await self.session.commit()

        return len(logs)
    async def export(
        self,
        *,
        start: datetime,
        end: datetime,
    ):

        return await self.between(
            start,
            end,
        )
    async def statistics(self):

        total = await self.count()

        today = datetime.now(
            UTC,
        ).date()

        today_stmt = (
            select(func.count())
            .select_from(AuditLog)
            .where(
                func.date(
                    AuditLog.created_at
                )
                == today
            )
        )

        today_logs = (
            await self.session.execute(
                today_stmt
            )
        ).scalar_one()

        return {

            "total": total,

            "today": today_logs,
        }