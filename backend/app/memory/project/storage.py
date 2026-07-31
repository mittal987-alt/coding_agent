from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime

from .models import (
    ProjectConvention,
    ProjectDecision,
    ProjectDependency,
    ProjectFile,
    ProjectMemory,
    ProjectStatistics,
)


class BaseProjectStorage(ABC):
    """
    Abstract storage backend for project memory.
    """

    @abstractmethod
    async def create(
        self,
        project: ProjectMemory,
    ) -> ProjectMemory:
        ...

    @abstractmethod
    async def get(
        self,
        project_id: str,
    ) -> ProjectMemory | None:
        ...

    @abstractmethod
    async def update(
        self,
        project: ProjectMemory,
    ) -> ProjectMemory:
        ...

    @abstractmethod
    async def delete(
        self,
        project_id: str,
    ) -> bool:
        ...

    @abstractmethod
    async def list(
        self,
    ) -> list[ProjectMemory]:
        ...

    @abstractmethod
    async def statistics(
        self,
        project_id: str,
    ) -> ProjectStatistics:
        ...


class InMemoryProjectStorage(BaseProjectStorage):
    """
    Reference in-memory implementation.
    """

    def __init__(self) -> None:
        self._projects: dict[str, ProjectMemory] = {}

    async def create(
        self,
        project: ProjectMemory,
    ) -> ProjectMemory:

        self._projects[project.id] = project

        return project

    async def get(
        self,
        project_id: str,
    ) -> ProjectMemory | None:

        return self._projects.get(project_id)

    async def update(
        self,
        project: ProjectMemory,
    ) -> ProjectMemory:

        project.updated_at = datetime.now(UTC)

        self._projects[project.id] = project

        return project

    async def delete(
        self,
        project_id: str,
    ) -> bool:

        return self._projects.pop(project_id, None) is not None

    async def list(
        self,
    ) -> list[ProjectMemory]:

        return sorted(
            self._projects.values(),
            key=lambda p: p.updated_at,
            reverse=True,
        )

    async def statistics(
        self,
        project_id: str,
    ) -> ProjectStatistics:

        project = self._projects[project_id]

        frontend = len(project.architecture.frontend)
        backend = len(project.architecture.backend)
        databases = len(project.architecture.databases)
        ai_stack = len(project.architecture.ai_stack)

        return ProjectStatistics(
            project_id=project.id,
            total_files=len(project.files),
            total_dependencies=len(project.dependencies),
            total_decisions=len(project.decisions),
            total_conventions=len(project.conventions),
            frontend_frameworks=frontend,
            backend_frameworks=backend,
            databases=databases,
            ai_components=ai_stack,
            last_updated=project.updated_at,
        )

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------

    async def add_file(
        self,
        project_id: str,
        file: ProjectFile,
    ) -> None:

        self._projects[project_id].files.append(file)

    async def remove_file(
        self,
        project_id: str,
        file_path: str,
    ) -> bool:

        project = self._projects[project_id]

        before = len(project.files)

        project.files = [
            f
            for f in project.files
            if f.path != file_path
        ]

        return len(project.files) != before

    # ------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------

    async def add_dependency(
        self,
        project_id: str,
        dependency: ProjectDependency,
    ) -> None:

        self._projects[project_id].dependencies.append(
            dependency
        )

    async def remove_dependency(
        self,
        project_id: str,
        name: str,
    ) -> bool:

        project = self._projects[project_id]

        before = len(project.dependencies)

        project.dependencies = [
            d
            for d in project.dependencies
            if d.name != name
        ]

        return len(project.dependencies) != before

    # ------------------------------------------------------------------
    # Conventions
    # ------------------------------------------------------------------

    async def add_convention(
        self,
        project_id: str,
        convention: ProjectConvention,
    ) -> None:

        self._projects[project_id].conventions.append(
            convention
        )

    # ------------------------------------------------------------------
    # Decisions
    # ------------------------------------------------------------------

    async def add_decision(
        self,
        project_id: str,
        decision: ProjectDecision,
    ) -> None:

        self._projects[project_id].decisions.append(
            decision
        )