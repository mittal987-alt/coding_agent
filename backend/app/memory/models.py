from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """
    Supported memory categories.
    """

    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    VECTOR = "vector"
    DECISION = "decision"
    CONVERSATION = "conversation"
    PROJECT = "project"


class MemoryStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MemoryDocument(BaseModel):
    """
    Canonical memory object stored by the system.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    memory_type: MemoryType

    title: str

    content: str

    summary: str | None = None

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    embedding_id: str | None = None

    project_id: str | None = None

    conversation_id: str | None = None

    parent_id: str | None = None

    related_memories: list[str] = Field(default_factory=list)

    importance: float = 0.5

    confidence: float = 1.0

    access_count: int = 0

    last_accessed_at: datetime | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    updated_at: datetime = Field(default_factory=datetime.utcnow)

    expires_at: datetime | None = None

    status: MemoryStatus = MemoryStatus.ACTIVE


class MemoryQuery(BaseModel):
    """
    Search request.
    """

    query: str

    memory_types: list[MemoryType] = Field(default_factory=list)

    project_id: str | None = None

    conversation_id: str | None = None

    tags: list[str] = Field(default_factory=list)

    limit: int = 10

    min_score: float = 0.0

    include_archived: bool = False

    metadata_filters: dict[str, Any] = Field(default_factory=dict)


class MemoryResult(BaseModel):
    """
    Search result returned to an agent.
    """

    document: MemoryDocument

    score: float

    semantic_score: float = 0.0

    vector_score: float = 0.0

    keyword_score: float = 0.0

    rerank_score: float = 0.0


class MemoryRelationship(BaseModel):
    """
    Relationship between two memories.
    """

    source_id: str

    target_id: str

    relationship: str

    weight: float = 1.0


class MemoryStatistics(BaseModel):
    """
    Memory system metrics.
    """

    total_documents: int = 0

    episodic_documents: int = 0

    semantic_documents: int = 0

    vector_documents: int = 0

    project_documents: int = 0

    conversation_documents: int = 0

    decision_documents: int = 0

    average_importance: float = 0.0

    average_access_count: float = 0.0

    storage_size_mb: float = 0.0

    embedding_count: int = 0