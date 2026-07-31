from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.repositories.base import BaseRepository
class WorkspaceRepository(BaseRepository[Workspace]):
    """
    Repository for workspace persistence.
    """

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:

        super().__init__(
            session=session,
            model=Workspace,
        )
    async def get_by_path(
        self,
        path: str,
    ) -> Workspace | None:

        stmt = select(Workspace).where(
            Workspace.path == path
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
    async def by_project(
        self,
        project_id: str,
    ) -> Sequence[Workspace]:

        stmt = (
            select(Workspace)
            .where(
                Workspace.project_id == project_id
            )
            .order_by(
                Workspace.updated_at.desc()
            )
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def search(
        self,
        query: str,
        limit: int = 20,
    ) -> Sequence[Workspace]:

        stmt = (

            select(Workspace)

            .where(

                or_(

                    Workspace.name.ilike(
                        f"%{query}%"
                    ),

                    Workspace.path.ilike(
                        f"%{query}%"
                    ),
                )
            )

            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def update_branch(
        self,
        workspace_id: str,
        branch: str,
    ):

        await self.session.execute(

            update(Workspace)

            .where(
                Workspace.id == workspace_id
            )

            .values(
                current_branch=branch,
            )
        )

        await self.session.commit() 
    async def update_last_commit(
        self,
        workspace_id: str,
        commit_hash: str,
    ):

        await self.session.execute(

            update(Workspace)

            .where(
                Workspace.id == workspace_id
            )

            .values(
                last_commit=commit_hash,
            )
        )

        await self.session.commit()
    async def update_index_status(
        self,
        workspace_id: str,
        indexed: bool,
    ):

        await self.session.execute(

            update(Workspace)

            .where(
                Workspace.id == workspace_id
            )

            .values(
                indexed=indexed,
            )
        )

        await self.session.commit()
    async def update_open_files(
        self,
        workspace_id: str,
        files: list[str],
    ):

        await self.session.execute(

            update(Workspace)

            .where(
                Workspace.id == workspace_id
            )

            .values(
                open_files=files,
            )
        )

        await self.session.commit()
    async def update_sync_status(
        self,
        workspace_id: str,
        synced: bool,
    ):

        await self.session.execute(

            update(Workspace)

            .where(
                Workspace.id == workspace_id
            )

            .values(
                synced=synced,
            )
        )

        await self.session.commit()
    async def recent(
        self,
        limit: int = 20,
    ):

        stmt = (
            select(Workspace)
            .order_by(
                Workspace.updated_at.desc()
            )
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def indexed(self):

        stmt = select(Workspace).where(
            Workspace.indexed.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def active(self):

        stmt = select(Workspace).where(
            Workspace.is_active.is_(True)
        )

        result = await self.session.execute(stmt)

        return result.scalars().all()
    async def statistics(self):

        total = await self.count()

        indexed_stmt = (
            select(func.count())
            .select_from(Workspace)
            .where(
                Workspace.indexed.is_(True)
            )
        )

        indexed = (
            await self.session.execute(
                indexed_stmt
            )
        ).scalar_one()

        active_stmt = (
            select(func.count())
            .select_from(Workspace)
            .where(
                Workspace.is_active.is_(True)
            )
        )

        active = (
            await self.session.execute(
                active_stmt
            )
        ).scalar_one()

        return {
            "total": total,
            "indexed": indexed,
            "active": active,
        }