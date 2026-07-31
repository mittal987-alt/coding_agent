from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------


class ArchitectureType(str, Enum):
    """Supported software architectures."""

    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"
    MODULAR_MONOLITH = "modular_monolith"
    LAYERED = "layered"
    CLEAN = "clean"
    HEXAGONAL = "hexagonal"
    UNKNOWN = "unknown"


class DependencyType(str, Enum):
    """Dependency categories."""

    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    CLOUD = "cloud"
    DEV_TOOL = "dev_tool"
    AI_MODEL = "ai_model"
    SERVICE = "service"
    OTHER = "other"


class FileType(str, Enum):
    """Project file types."""

    SOURCE = "source"
    CONFIG = "config"
    TEST = "test"
    DOCUMENTATION = "documentation"
    SCRIPT = "script"
    ASSET = "asset"
    OTHER = "other"


class DecisionStatus(str, Enum):
    """Architecture decision status."""

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


# ----------------------------------------------------------------------
# Project Architecture
# ----------------------------------------------------------------------


class ProjectArchitecture(BaseModel):
    """
    High-level architecture information.
    """

    architecture_type: ArchitectureType = ArchitectureType.UNKNOWN

    frontend: list[str] = Field(default_factory=list)

    backend: list[str] = Field(default_factory=list)

    databases: list[str] = Field(default_factory=list)

    ai_stack: list[str] = Field(default_factory=list)

    infrastructure: list[str] = Field(default_factory=list)

    deployment: list[str] = Field(default_factory=list)

    description: str = ""


# ----------------------------------------------------------------------
# Files
# ----------------------------------------------------------------------


class ProjectFile(BaseModel):
    """
    Represents a tracked project file.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    path: str

    file_type: FileType

    language: str | None = None

    description: str = ""

    imports: list[str] = Field(default_factory=list)

    exports: list[str] = Field(default_factory=list)

    referenced_files: list[str] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    last_modified: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ----------------------------------------------------------------------
# Dependencies
# ----------------------------------------------------------------------


class ProjectDependency(BaseModel):
    """
    External dependency.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    version: str | None = None

    dependency_type: DependencyType

    description: str = ""

    required: bool = True

    metadata: dict[str, Any] = Field(default_factory=dict)


# ----------------------------------------------------------------------
# Design Decisions
# ----------------------------------------------------------------------


class ProjectDecision(BaseModel):
    """
    Architecture Decision Record (ADR).
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    rationale: str = ""

    consequences: str = ""

    status: DecisionStatus = DecisionStatus.ACCEPTED

    related_files: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ----------------------------------------------------------------------
# Coding Conventions
# ----------------------------------------------------------------------


class ProjectConvention(BaseModel):
    """
    Coding conventions and standards.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    category: str

    title: str

    description: str

    examples: list[str] = Field(default_factory=list)


# ----------------------------------------------------------------------
# Project Memory
# ----------------------------------------------------------------------


class ProjectMemory(BaseModel):
    """
    Complete project knowledge.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    description: str = ""

    repository: str | None = None

    branch: str | None = None

    architecture: ProjectArchitecture = Field(
        default_factory=ProjectArchitecture
    )

    files: list[ProjectFile] = Field(default_factory=list)

    dependencies: list[ProjectDependency] = Field(default_factory=list)

    conventions: list[ProjectConvention] = Field(default_factory=list)

    decisions: list[ProjectDecision] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# ----------------------------------------------------------------------
# Statistics
# ----------------------------------------------------------------------


class ProjectStatistics(BaseModel):
    """
    Project analytics.
    """

    project_id: str

    total_files: int

    total_dependencies: int

    total_decisions: int

    total_conventions: int

    frontend_frameworks: int

    backend_frameworks: int

    databases: int

    ai_components: int

    last_updated: datetime