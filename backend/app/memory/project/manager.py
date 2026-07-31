# project/manager.py
from __future__ import annotations

import logging
from datetime import UTC, datetime

from .models import (
    ArchitectureType,
    ProjectArchitecture,
    ProjectConvention,
    ProjectDecision,
    ProjectDependency,
    ProjectFile,
    ProjectMemory,
    ProjectStatistics,
)
from .storage import BaseProjectStorage

logger = logging.getLogger(__name__)


class ProjectMemoryManager:
    """
    High-level manager for project memory.

    Responsibilities:
    - Project lifecycle
    - Repository knowledge
    - File indexing
    - Dependency tracking
    - Architecture management
    - Coding conventions
    - ADRs
    """

    def __init__(
        self,
        storage: BaseProjectStorage,
    ) -> None:

        self.storage = storage

    # ----------------------------------------------------------
    # Project Lifecycle
    # ----------------------------------------------------------

    async def create_project(
        self,
        *,
        name: str,
        description: str = "",
        repository: str | None = None,
        branch: str | None = None,
    ) -> ProjectMemory:

        project = ProjectMemory(
            name=name,
            description=description,
            repository=repository,
            branch=branch,
        )

        return await self.storage.create(project)

    async def get_project(
        self,
        project_id: str,
    ) -> ProjectMemory | None:

        return await self.storage.get(project_id)

    async def list_projects(
        self,
    ) -> list[ProjectMemory]:

        return await self.storage.list()

    async def delete_project(
        self,
        project_id: str,
    ) -> bool:

        return await self.storage.delete(project_id)

    # ----------------------------------------------------------
    # Architecture
    # ----------------------------------------------------------

    async def update_architecture(
        self,
        project_id: str,
        architecture: ProjectArchitecture,
    ) -> None:

        project = await self.storage.get(project_id)

        if project is None:
            raise ValueError("Project not found")

        project.architecture = architecture
        project.updated_at = datetime.now(UTC)

        await self.storage.update(project)

    async def set_architecture_type(
        self,
        project_id: str,
        architecture: ArchitectureType,
    ) -> None:

        project = await self.storage.get(project_id)

        if project is None:
            raise ValueError("Project not found")

        project.architecture.architecture_type = architecture
        project.updated_at = datetime.now(UTC)

        await self.storage.update(project)

    # ----------------------------------------------------------
    # Files
    # ----------------------------------------------------------

    async def add_file(
        self,
        project_id: str,
        file: ProjectFile,
    ) -> None:

        await self.storage.add_file(
            project_id,
            file,
        )

    async def remove_file(
        self,
        project_id: str,
        file_path: str,
    ) -> bool:

        return await self.storage.remove_file(
            project_id,
            file_path,
        )

    async def find_file(
        self,
        project_id: str,
        path: str,
    ) -> ProjectFile | None:

        project = await self.storage.get(project_id)

        if project is None:
            return None

        for file in project.files:

            if file.path == path:

                return file

        return None

    # ----------------------------------------------------------
    # Dependencies
    # ----------------------------------------------------------

    async def add_dependency(
        self,
        project_id: str,
        dependency: ProjectDependency,
    ) -> None:

        await self.storage.add_dependency(
            project_id,
            dependency,
        )

    async def remove_dependency(
        self,
        project_id: str,
        name: str,
    ) -> bool:

        return await self.storage.remove_dependency(
            project_id,
            name,
        )

    # ----------------------------------------------------------
    # Conventions
    # ----------------------------------------------------------

    async def add_convention(
        self,
        project_id: str,
        convention: ProjectConvention,
    ) -> None:

        await self.storage.add_convention(
            project_id,
            convention,
        )

    # ----------------------------------------------------------
    # Decisions (ADR)
    # ----------------------------------------------------------

    async def add_decision(
        self,
        project_id: str,
        decision: ProjectDecision,
    ) -> None:

        await self.storage.add_decision(
            project_id,
            decision,
        )

    # ----------------------------------------------------------
    # Search
    # ----------------------------------------------------------

    async def search_files(
        self,
        project_id: str,
        query: str,
    ) -> list[ProjectFile]:

        project = await self.storage.get(project_id)

        if project is None:
            return []

        query = query.lower()

        return [
            file
            for file in project.files
            if query in file.path.lower()
            or query in file.description.lower()
        ]

    async def search_dependencies(
        self,
        project_id: str,
        query: str,
    ) -> list[ProjectDependency]:

        project = await self.storage.get(project_id)

        if project is None:
            return []

        query = query.lower()

        return [
            dependency
            for dependency in project.dependencies
            if query in dependency.name.lower()
        ]

    # ----------------------------------------------------------
    # Statistics
    # ----------------------------------------------------------

    async def statistics(
        self,
        project_id: str,
    ) -> ProjectStatistics:

        return await self.storage.statistics(
            project_id
        )

    # ----------------------------------------------------------
    # Context Builder
    # ----------------------------------------------------------

    async def build_context(
        self,
        project_id: str,
    ) -> dict:

        project = await self.storage.get(project_id)

        if project is None:
            raise ValueError("Project not found")

        return {
            "name": project.name,
            "description": project.description,
            "architecture": project.architecture.model_dump(),
            "dependencies": [
                dependency.model_dump()
                for dependency in project.dependencies
            ],
            "files": [
                file.model_dump()
                for file in project.files
            ],
            "conventions": [
                convention.model_dump()
                for convention in project.conventions
            ],
            "decisions": [
                decision.model_dump()
                for decision in project.decisions
            ],
        }