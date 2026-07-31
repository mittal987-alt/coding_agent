from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric
from app.repositories.base import BaseRepository

class MetricsRepository(BaseRepository[Metric]):
    """
    Repository for application metrics.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Metric,
        )
    async def record(
        self,
        *,
        name: str,
        value: float,
        tags: dict | None = None,
    ):

        return await self.create(

            name=name,

            value=value,

            tags=tags or {},

            timestamp=datetime.now(UTC),
        )
    async def by_name(
        self,
        name: str,
    ) -> Sequence[Metric]:

        stmt = (
            select(Metric)
            .where(
                Metric.name == name
            )
            .order_by(
                Metric.timestamp.desc()
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def between(
        self,
        start: datetime,
        end: datetime,
    ):

        stmt = (
            select(Metric)
            .where(
                Metric.timestamp.between(
                    start,
                    end,
                )
            )
            .order_by(
                Metric.timestamp.asc()
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def average(
        self,
        name: str,
    ):

        stmt = (
            select(
                func.avg(
                    Metric.value
                )
            )
            .where(
                Metric.name == name
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar()
    async def maximum(
        self,
        name: str,
    ):

        stmt = (
            select(
                func.max(
                    Metric.value
                )
            )
            .where(
                Metric.name == name
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar()
    async def minimum(
        self,
        name: str,
    ):

        stmt = (
            select(
                func.min(
                    Metric.value
                )
            )
            .where(
                Metric.name == name
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar()
    async def latest(
        self,
        name: str,
    ):

        stmt = (
            select(Metric)
            .where(
                Metric.name == name
            )
            .order_by(
                Metric.timestamp.desc()
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    async def total_tokens(self):

        stmt = (
            select(
                func.sum(
                    Metric.value
                )
            )
            .where(
                Metric.name == "tokens"
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar() or 0
    async def total_cost(self):

        stmt = (
            select(
                func.sum(
                    Metric.value
                )
            )
            .where(
                Metric.name == "cost"
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar() or 0 
    async def total_errors(self):

        stmt = (
            select(
                func.count()
            )
            .select_from(Metric)
            .where(
                Metric.name == "error"
            )
        )

        result = await self.session.execute(stmt)

        return result.scalar_one()
    async def dashboard(self):

        return {

            "tokens": await self.total_tokens(),

            "cost": await self.total_cost(),

            "errors": await self.total_errors(),
        }
    async def statistics(self):

        total = await self.count()

        return {

            "metrics": total,

            "dashboard": await self.dashboard(),
        }