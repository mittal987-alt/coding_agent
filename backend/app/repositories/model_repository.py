from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.model import Model
from app.repositories.base import BaseRepository
class ModelRepository(BaseRepository[Model]):
    """
    Repository responsible for AI model persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Model,
        )
    async def get_by_name(
        self,
        name: str,
    ) -> Model | None:

        stmt = select(Model).where(
            Model.name == name
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    async def by_provider(
        self,
        provider: str,
    ) -> Sequence[Model]:

        stmt = (
            select(Model)
            .where(
                Model.provider == provider
            )
            .order_by(Model.name)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[Model]:

        stmt = (

            select(Model)

            .where(

                or_(

                    Model.name.ilike(
                        f"%{query}%"
                    ),

                    Model.provider.ilike(
                        f"%{query}%"
                    ),

                    Model.description.ilike(
                        f"%{query}%"
                    ),
                )
            )

            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def available(self):

        stmt = select(Model).where(
            Model.available.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def defaults(self):

        stmt = select(Model).where(
            Model.is_default.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def vision_models(self):

        stmt = select(Model).where(
            Model.supports_vision.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def function_calling_models(self):

        stmt = select(Model).where(
            Model.supports_functions.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()   
    async def update_availability(
        self,
        model_id: str,
        available: bool,
    ):

        await self.session.execute(

            update(Model)

            .where(
                Model.id == model_id
            )

            .values(
                available=available,
            )
        )

        await self.session.commit()
    async def update_pricing(
        self,
        model_id: str,
        input_price: float,
        output_price: float,
    ):

        await self.session.execute(

            update(Model)

            .where(
                Model.id == model_id
            )

            .values(

                input_price=input_price,

                output_price=output_price,
            )
        )

        await self.session.commit()
    async def update_context_window(
        self,
        model_id: str,
        tokens: int,
    ):

        await self.session.execute(

            update(Model)

            .where(
                Model.id == model_id
            )

            .values(
                context_window=tokens,
            )
        )

        await self.session.commit()
    async def set_default(
        self,
        model_id: str,
    ):

        await self.session.execute(
            update(Model).values(
                is_default=False,
            )
        )

        await self.session.execute(

            update(Model)

            .where(
                Model.id == model_id
            )

            .values(
                is_default=True,
            )
        )

        await self.session.commit()

    async def statistics(self):

        total = await self.count()

        available = (

            await self.session.execute(

                select(func.count())

                .select_from(Model)

                .where(
                    Model.available.is_(True)
                )

            )

        ).scalar_one()

        defaults = (

            await self.session.execute(

                select(func.count())

                .select_from(Model)

                .where(
                    Model.is_default.is_(True)
                )

            )

        ).scalar_one()

        return {

            "total": total,

            "available": available,

            "default": defaults,
        }