from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

# pyrefly: ignore [missing-import]
from app.models.user import User
from app.repositories.base import Base
class UserRepository(Base[User]):
    """
    Repository for User persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):

        super().__init__(
            session=session,
            model=User,
        )
class UserRepository(BaseRepository[User]):
    """
    Repository for User persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ):

        super().__init__(
            session=session,
            model=User,
        )
    async def get_by_email(
        self,
        email: str,
    ) -> User | None:

        stmt = (
            select(User)
            .where(
                func.lower(User.email)
                == email.lower()
            )
        )

        result = await self.session.execute(
            stmt,
        )

        return result.scalar_one_or_none()
    async def get_by_username(
        self,
        username: str,
    ) -> User | None:

        stmt = select(User).where(
            User.username == username
        )

        result = await self.session.execute(
            stmt,
        )

        return result.scalar_one_or_none()
    async def email_exists(
        self,
        email: str,
    ) -> bool:

        return (
            await self.get_by_email(email)
        ) is not None
    async def username_exists(
        self,
        username: str,
    ) -> bool:

        return (
            await self.get_by_username(
                username
            )
        ) is not None
    async def verify_email(
        self,
        user_id: str,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                email_verified=True,
            )
        )

        await self.session.commit()
    async def update_password(
        self,
        user_id: str,
        password_hash: str,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                password_hash=password_hash,
            )
        )

        await self.session.commit() 
    async def update_refresh_token(
        self,
        user_id: str,
        refresh_token: str | None,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                refresh_token=refresh_token,
            )
        )

        await self.session.commit()
    async def update_role(
        self,
        user_id: str,
        role: str,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                role=role,
            )
        )

        await self.session.commit()
    async def update_role(
        self,
        user_id: str,
        role: str,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                role=role,
            )
        )

        await self.session.commit()
    async def activate(
        self,
        user_id: str,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                is_active=True,
            )
        )

        await self.session.commit()
    async def deactivate(
        self,
        user_id: str,
    ):

        await self.session.execute(

            update(User)

            .where(User.id == user_id)

            .values(
                is_active=False,
            )
        )

        await self.session.commit()
            async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[User]:

        stmt = (

            select(User)

            .where(

                or_(

                    User.name.ilike(
                        f"%{query}%"
                    ),

                    User.email.ilike(
                        f"%{query}%"
                    ),

                    User.username.ilike(
                        f"%{query}%"
                    ),
                )
            )

            .limit(limit)
        )

        result = await self.session.execute(
            stmt,
        )

        return result.scalars().all()
    async def by_role(
        self,
        role: str,
    ):

        stmt = select(User).where(
            User.role == role
        )

        result = await self.session.execute(
            stmt,
        )

        return result.scalars().all()
    async def active_users(self):

        stmt = select(User).where(
            User.is_active.is_(True)
        )

        result = await self.session.execute(
            stmt,
        )

        return result.scalars().all()
    async def recent(
        self,
        limit: int = 20,
    ):

        stmt = (

            select(User)

            .order_by(
                User.created_at.desc()
            )

            .limit(limit)
        )

        result = await self.session.execute(
            stmt,
        )

        return result.scalars().all()
    async def statistics(self):

        total = await self.count()

        active = len(
            await self.active_users()
        )

        verified = len(

            (
                await self.session.execute(

                    select(User).where(

                        User.email_verified.is_(
                            True
                        )
                    )
                )
            )

            .scalars()

            .all()
        )

        return {

            "total": total,

            "active": active,

            "verified": verified,
        }