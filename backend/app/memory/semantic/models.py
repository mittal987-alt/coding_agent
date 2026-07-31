from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class KnowledgeCategory(str, Enum):
    """
    Categories of semantic knowledge.
    """

    ARCHITECTURE = "architecture"
    FRAMEWORK = "framework"
    API = "api"
    DATABASE = "database"
    SECURITY = "security"
    DESIGN_PATTERN = "design_pattern"
    BEST_PRACTICE = "best_practice"
    ALGORITHM = "algorithm"
    TOOL = "tool"
    WORKFLOW = "workflow"
    DOCUMENTATION = "documentation"
    DOMAIN = "domain"
    OTHER = "other"


class KnowledgeSource(str, Enum):
    """
    Origin of the knowledge.
    """

    USER = "user"
    DOCUMENTATION = "documentation"
    CODEBASE = "codebase"
    EPISODIC_MEMORY = "episodic_memory"
    REPOSITORY_ANALYSIS = "repository_analysis"
    LLM_GENERATED = "llm_generated"
    WEB = "web"
    MANUAL = "manual"


class KnowledgeRelationshipType(str, Enum):
    """
    Relationship between knowledge entries.
    """

    RELATED = "related"
    DEPENDS_ON = "depends_on"
    EXTENDS = "extends"
    REPLACES = "replaces"
    CONFLICTS_WITH = "conflicts_with"
    REFERENCES = "references"


class KnowledgeReference(BaseModel):
    """
    External or internal reference for a knowledge entry.
    """

    title: str

    reference_type: str

    uri: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeRelationship(BaseModel):
    """
    Relationship to another knowledge entry.
    """

    target_id: str

    relationship: KnowledgeRelationshipType

    weight: float = 1.0


class SemanticMemory(BaseModel):
    """
    Long-term factual knowledge.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    summary: str

    content: str

    category: KnowledgeCategory

    source: KnowledgeSource

    confidence: float = 1.0

    importance: float = 1.0

    project_id: str | None = None

    tags: list[str] = Field(default_factory=list)

    references: list[
        KnowledgeReference
    ] = Field(default_factory=list)

    relationships: list[
        KnowledgeRelationship
    ] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    embedding_id: str | None = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    last_accessed_at: datetime | None = None

    access_count: int = 0

    verified: bool = False