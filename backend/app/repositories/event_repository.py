from __future__ import annotations

from datetime import UTC, datetime
from typing import Sequence

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event
from app.repositories.base import BaseRepository
class EventRepository(BaseRepository[Event]):
    """
    Repository for persistent event storage.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Event,
        )
    async def save(
        self,
        *,
        event: str,
        payload: dict,
    ) -> Event:

        return await self.create(
            name=event,
            payload=payload,
            created_at=datetime.now(UTC),
        )
    async def load(
        self,
        event: str,
    ) -> Sequence[Event]:

        stmt = (
            select(Event)
            .where(Event.name == event)
            .order_by(Event.created_at.asc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def history(
        self,
        limit: int = 100,
    ):

        stmt = (
            select(Event)
            .order_by(Event.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def by_type(
        self,
        event: str,
    ):

        return await self.load(event)
    async def between(
        self,
        start: datetime,
        end: datetime,
    ):

        stmt = (
            select(Event)
            .where(
                Event.created_at.between(
                    start,
                    end,
                )
            )
            .order_by(Event.created_at.asc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()   
    async def after(
        self,
        event_id: str,
    ):

        stmt = (
            select(Event)
            .where(Event.id > event_id)
            .order_by(Event.created_at.asc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()   
    async def by_aggregate(
        self,
        aggregate_id: str,
    ):

        stmt = (
            select(Event)
            .where(
                Event.aggregate_id == aggregate_id
            )
            .order_by(Event.created_at.asc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()



    async def filter(
        self,
        *,
        event: str | None = None,
        aggregate_id: str | None = None,
        limit: int = 100,
    ):

        stmt = select(Event)

        filters = []

        if event:
            filters.append(
                Event.name == event
            )

        if aggregate_id:
            filters.append(
                Event.aggregate_id == aggregate_id
            )

        if filters:
            stmt = stmt.where(
                and_(*filters)
            )

        stmt = (
            stmt
            .order_by(Event.created_at.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def clear(self):

        events = (
            await self.session.execute(
                select(Event)
            )
        ).scalars().all()

        for event in events:
            await self.session.delete(event)

        await self.session.commit()

        return len(events)
    async def replay(
        self,
        event: str,
    ):

        return await self.load(event)
    async def statistics(self):

        total = await self.count()

        unique_stmt = (
            select(
                func.count(
                    func.distinct(Event.name)
                )
            )
        )

        event_types = (
            await self.session.execute(
                unique_stmt
            )
        ).scalar_one()

        return {

            "total": total,

            "event_types": event_types,
        }