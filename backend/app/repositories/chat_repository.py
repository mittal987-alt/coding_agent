from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat import Chat
from app.repositories.base import BaseRepository

class ChatRepository(BaseRepository[Chat]):
    """
    Repository for chat conversations.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Chat,
        )
    async def get_conversation(
        self,
        conversation_id: str,
    ) -> Chat | None:

        stmt = select(Chat).where(
            Chat.id == conversation_id
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    async def by_user(
        self,
        user_id: str,
    ) -> Sequence[Chat]:

        stmt = (
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def by_project(
        self,
        project_id: str,
    ) -> Sequence[Chat]:

        stmt = (
            select(Chat)
            .where(Chat.project_id == project_id)
            .order_by(Chat.updated_at.desc())
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[Chat]:

        stmt = (

            select(Chat)

            .where(

                or_(

                    Chat.title.ilike(
                        f"%{query}%"
                    ),

                    Chat.summary.ilike(
                        f"%{query}%"
                    ),
                )
            )

            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()   
    async def rename(
        self,
        conversation_id: str,
        title: str,
    ):

        await self.session.execute(

            update(Chat)

            .where(
                Chat.id == conversation_id
            )

            .values(
                title=title,
            )
        )

        await self.session.commit()
    async def rename(
        self,
        conversation_id: str,
        title: str,
    ):

        await self.session.execute(

            update(Chat)

            .where(
                Chat.id == conversation_id
            )

            .values(
                title=title,
            )
        )

        await self.session.commit()
    async def update_summary(
        self,
        conversation_id: str,
        summary: str,
    ):

        await self.session.execute(

            update(Chat)

            .where(
                Chat.id == conversation_id
            )

            .values(
                summary=summary,
            )
        )

        await self.session.commit()
    async def update_tokens(
        self,
        conversation_id: str,
        input_tokens: int,
        output_tokens: int,
    ):

        conversation = await self.get(conversation_id)

        if conversation is None:
            return

        await self.session.execute(

            update(Chat)

            .where(
                Chat.id == conversation_id
            )

            .values(

                input_tokens=conversation.input_tokens + input_tokens,

                output_tokens=conversation.output_tokens + output_tokens,
            )
        )

        await self.session.commit()
    async def set_streaming(
        self,
        conversation_id: str,
        streaming: bool,
    ):

        await self.session.execute(

            update(Chat)

            .where(
                Chat.id == conversation_id
            )

            .values(
                streaming=streaming,
            )
        )

        await self.session.commit()
    async def pin(
        self,
        conversation_id: str,
    ):

        await self.session.execute(

            update(Chat)

            .where(Chat.id == conversation_id)

            .values(
                pinned=True,
            )
        )

        await self.session.commit()
    async def archive(
        self,
        conversation_id: str,
    ):

        await self.session.execute(

            update(Chat)

            .where(Chat.id == conversation_id)

            .values(
                archived=True,
            )
        )

        await self.session.commit()
    async def recent(
        self,
        limit: int = 20,
    ):

        stmt = (

            select(Chat)

            .order_by(
                Chat.updated_at.desc()
            )

            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
        async def active(self):

        stmt = select(Chat).where(
            Chat.archived.is_(False)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def statistics(self):

        total = await self.count()

        archived_stmt = (
            select(func.count())
            .select_from(Chat)
            .where(Chat.archived.is_(True))
        )

        archived = (
            await self.session.execute(
                archived_stmt
            )
        ).scalar_one()

        pinned_stmt = (
            select(func.count())
            .select_from(Chat)
            .where(Chat.pinned.is_(True))
        )

        pinned = (
            await self.session.execute(
                pinned_stmt
            )
        ).scalar_one()

        return {

            "total": total,

            "active": total - archived,

            "archived": archived,

            "pinned": pinned,
        }
    async def statistics(self):

        total = await self.count()

        archived_stmt = (
            select(func.count())
            .select_from(Chat)
            .where(Chat.archived.is_(True))
        )

        archived = (
            await self.session.execute(
                archived_stmt
            )
        ).scalar_one()

        pinned_stmt = (
            select(func.count())
            .select_from(Chat)
            .where(Chat.pinned.is_(True))
        )

        pinned = (
            await self.session.execute(
                pinned_stmt
            )
        ).scalar_one()

        return {

            "total": total,

            "active": total - archived,

            "archived": archived,

            "pinned": pinned,
        }