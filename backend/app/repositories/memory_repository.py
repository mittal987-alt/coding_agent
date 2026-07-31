from __future__ import annotations

from typing import Sequence

from sqlalchemy import desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import Memory
from app.repositories.base import BaseRepository
class MemoryRepository(BaseRepository[Memory]):
    """
    Repository responsible for long-term AI memory.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Memory,
        )
    async def by_user(
        self,
        user_id: str,
    ) -> Sequence[Memory]:

        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(desc(Memory.importance))
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def by_project(
        self,
        project_id: str,
    ) -> Sequence[Memory]:

        stmt = (
            select(Memory)
            .where(Memory.project_id == project_id)
            .order_by(desc(Memory.updated_at))
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[Memory]:

        stmt = (

            select(Memory)

            .where(

                or_(

                    Memory.title.ilike(
                        f"%{query}%"
                    ),

                    Memory.content.ilike(
                        f"%{query}%"
                    ),
                )
            )

            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def important(
        self,
        minimum_score: float = 0.8,
    ):

        stmt = (

            select(Memory)

            .where(
                Memory.importance >= minimum_score
            )

            .order_by(
                Memory.importance.desc()
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def update_embedding(
        self,
        memory_id: str,
        embedding_id: str,
    ):

        await self.session.execute(

            update(Memory)

            .where(
                Memory.id == memory_id
            )

            .values(
                embedding_id=embedding_id,
            )
        )

        await self.session.commit()
    async def increase_importance(
        self,
        memory_id: str,
        amount: float = 0.05,
    ):

        memory = await self.get(memory_id)

        if memory is None:
            return

        score = min(
            memory.importance + amount,
            1.0,
        )

        await self.session.execute(

            update(Memory)

            .where(
                Memory.id == memory_id
            )

            .values(
                importance=score,
            )
        )

        await self.session.commit()
    async def accessed(
        self,
        memory_id: str,
    ):

        memory = await self.get(memory_id)

        if memory is None:
            return

        await self.session.execute(

            update(Memory)

            .where(
                Memory.id == memory_id
            )

            .values(
                access_count=memory.access_count + 1,
            )
        )

        await self.session.commit()
    async def archive(
        self,
        memory_id: str,
    ):

        await self.session.execute(

            update(Memory)

            .where(
                Memory.id == memory_id
            )

            .values(
                archived=True,
            )
        )

        await self.session.commit()
    async def active(self):

        stmt = select(Memory).where(
            Memory.archived.is_(False)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def recent(
        self,
        limit: int = 20,
    ):

        stmt = (
            select(Memory)
            .order_by(
                Memory.updated_at.desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def statistics(self):

        total = await self.count()

        archived = (

            await self.session.execute(

                select(func.count())

                .select_from(Memory)

                .where(
                    Memory.archived.is_(True)
                )
            )

        ).scalar_one()

        important = (

            await self.session.execute(

                select(func.count())

                .select_from(Memory)

                .where(
                    Memory.importance >= 0.8
                )
            )

        ).scalar_one()

        return {

            "total": total,

            "active": total - archived,

            "archived": archived,

            "important": important,
        }