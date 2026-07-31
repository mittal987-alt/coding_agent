from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from app.api.schemas.common import (
    BaseSchema,
    TimestampSchema,
)
class MemoryCreateRequest(BaseSchema):
    """
    Store a memory.
    """

    session_id: str

    content: str = Field(
        min_length=1,
        max_length=50000,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    importance: float = Field(
        default=0.5,
        ge=0,
        le=1,
    )
class MemoryResponse(TimestampSchema):

    id: str

    session_id: str

    content: str

    memory_type: Literal[
        "short_term",
        "long_term",
        "episodic",
        "semantic",
    ]

    importance: float

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )
class MemorySearchRequest(BaseSchema):

    query: str

    limit: int = Field(
        default=10,
        ge=1,
        le=100,
    )

    minimum_score: float = Field(
        default=0.0,
        ge=0,
        le=1,
    )
class MemorySearchResult(BaseSchema):

    id: str

    score: float

    memory: MemoryResponse

class ConversationSummary(BaseSchema):

    session_id: str

    summary: str

    generated_at: datetime
class DemoteMemoryRequest(BaseSchema):

    memory_id: str
class DeleteMemoryRequest(BaseSchema):

    memory_id: str
class LongTermMemory(BaseSchema):

    id: str

    category: str

    title: str

    content: str

    relevance: float

    last_accessed: datetime
class ShortTermMemory(BaseSchema):

    id: str

    session_id: str

    messages: int

    token_count: int

    expires_at: datetime
class EmbeddingMetadata(BaseSchema):

    model: str

    dimensions: int

    vector_store: str
class EmbeddingResponse(BaseSchema):

    memory_id: str

    embedding_created: bool

    metadata: EmbeddingMetadata
class MemoryStatistics(BaseSchema):

    short_term_memories: int

    long_term_memories: int

    semantic_memories: int

    total_embeddings: int

    vector_store_size_mb: float
class MemoryEvent(BaseSchema):

    event: Literal[
        "created",
        "updated",
        "deleted",
        "promoted",
        "demoted",
        "summarized",
    ]

    memory_id: str

    session_id: str | None = None

    data: dict[str, Any] = Field(
        default_factory=dict,
    )
class MemoryContext(BaseSchema):

    session_id: str

    memories: list[MemoryResponse]

    summary: ConversationSummary | None = None
class MemoryImportRequest(BaseSchema):

    memories: list[MemoryCreateRequest]
class MemoryExportResponse(BaseSchema):

    exported_at: datetime

    total_memories: int

    memories: list[MemoryResponse]