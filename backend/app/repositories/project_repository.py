from __future__ import annotations

from typing import Sequence
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """
    Repository for project persistence.
    """

    def __init__(self, db: Session) -> None:
        super().__init__(db=db, model=Project)

    def get_by_id(self, project_id: int) -> Project | None:
        return self.get(project_id)

    def search(self, query: str, limit: int = 20) -> Sequence[Project]:
        return (
            self.db.query(Project)
            .filter(
                or_(
                    Project.name.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
            .all()
        )