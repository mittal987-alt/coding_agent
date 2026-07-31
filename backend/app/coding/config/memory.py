from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MemoryBackend = Literal[
    "sqlite",
    "postgres",
    "redis",
    "memory",
]

VectorBackend = Literal[
    "faiss",
    "chroma",
    "qdrant",
    "pinecone",
    "milvus",
    "none",
]

@dataclass(slots=True)
class EmbeddingConfig:
    """
    Embedding model configuration.
    """

    provider: str = "openai"

    model: str = "text-embedding-3-small"

    dimensions: int = 1536

    batch_size: int = 32

    normalize: bool = True

@dataclass(slots=True)
class VectorStoreConfig:
    """
    Semantic memory storage.
    """

    backend: VectorBackend = "faiss"

    collection_name: str = "memory"

    similarity_threshold: float = 0.75

    top_k: int = 10

    persist: bool = True

@dataclass(slots=True)
class ConversationMemoryConfig:
    """
    Conversation history configuration.
    """

    max_messages: int = 100

    max_tokens: int = 16000

    auto_summarize: bool = True

    summarize_after_messages: int = 50

    summarize_after_tokens: int = 12000

@dataclass(slots=True)
class LongTermMemoryConfig:
    """
    Long-term memory settings.
    """

    enabled: bool = True

    max_documents: int = 100000

    auto_index: bool = True

    deduplicate: bool = True

    semantic_search: bool = True

@dataclass(slots=True)
class RetrievalConfig:
    """
    Retrieval behavior.
    """

    top_k: int = 8

    rerank: bool = True

    score_threshold: float = 0.70

    include_metadata: bool = True

    max_context_chunks: int = 20

@dataclass(slots=True)
class PersistenceConfig:
    """
    Persistence settings.
    """

    backend: MemoryBackend = "sqlite"

    database_url: str | None = None

    autosave: bool = True

    autosave_interval: int = 60

    compress: bool = True

@dataclass(slots=True)
class RetentionConfig:
    """
    Memory retention policy.
    """

    conversation_days: int = 30

    long_term_days: int = 365

    delete_expired: bool = True

    cleanup_interval_hours: int = 24


@dataclass(slots=True)
class MemoryConfig:
    """
    Complete memory configuration.
    """

    embeddings: EmbeddingConfig = field(
        default_factory=EmbeddingConfig,
    )

    vector_store: VectorStoreConfig = field(
        default_factory=VectorStoreConfig,
    )

    conversation: ConversationMemoryConfig = field(
        default_factory=ConversationMemoryConfig,
    )

    long_term: LongTermMemoryConfig = field(
        default_factory=LongTermMemoryConfig,
    )

    retrieval: RetrievalConfig = field(
        default_factory=RetrievalConfig,
    )

    persistence: PersistenceConfig = field(
        default_factory=PersistenceConfig,
    )

    retention: RetentionConfig = field(
        default_factory=RetentionConfig,
    )
def create_memory_config() -> MemoryConfig:
    """
    Create the default memory configuration.
    """
    return MemoryConfig()
