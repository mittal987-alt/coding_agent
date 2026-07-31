# exceptions.py
"""
Custom exceptions for the Memory System.
"""

from __future__ import annotations

from typing import Any


class MemoryError(Exception):
    """
    Base exception for the memory subsystem.
    """

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class MemoryValidationError(MemoryError):
    """
    Raised when a memory document or query is invalid.
    """


class MemoryNotFoundError(MemoryError):
    """
    Raised when a memory document cannot be found.
    """

    def __init__(
        self,
        memory_id: str,
    ) -> None:
        super().__init__(
            f"Memory '{memory_id}' was not found.",
            details={"memory_id": memory_id},
        )


class MemoryAlreadyExistsError(MemoryError):
    """
    Raised when attempting to create a duplicate memory.
    """

    def __init__(
        self,
        memory_id: str,
    ) -> None:
        super().__init__(
            f"Memory '{memory_id}' already exists.",
            details={"memory_id": memory_id},
        )


class MemoryStorageError(MemoryError):
    """
    Raised when the storage backend fails.
    """


class MemoryConnectionError(MemoryStorageError):
    """
    Raised when the database or vector store is unavailable.
    """


class EmbeddingError(MemoryError):
    """
    Raised when embedding generation fails.
    """


class EmbeddingProviderError(EmbeddingError):
    """
    Raised when the embedding model/provider fails.
    """


class EmbeddingDimensionError(EmbeddingError):
    """
    Raised when embedding dimensions are incompatible.
    """

    def __init__(
        self,
        expected: int,
        received: int,
    ) -> None:
        super().__init__(
            (
                "Embedding dimension mismatch. "
                f"Expected {expected}, received {received}."
            ),
            details={
                "expected": expected,
                "received": received,
            },
        )


class RetrievalError(MemoryError):
    """
    Raised when retrieval fails.
    """


class RankingError(MemoryError):
    """
    Raised when reranking fails.
    """


class CacheError(MemoryError):
    """
    Raised when cache operations fail.
    """


class MemoryExpiredError(MemoryError):
    """
    Raised when an expired memory is accessed.
    """

    def __init__(
        self,
        memory_id: str,
    ) -> None:
        super().__init__(
            f"Memory '{memory_id}' has expired.",
            details={"memory_id": memory_id},
        )


class UnsupportedMemoryTypeError(MemoryError):
    """
    Raised when an unknown memory type is encountered.
    """

    def __init__(
        self,
        memory_type: str,
    ) -> None:
        super().__init__(
            f"Unsupported memory type '{memory_type}'.",
            details={
                "memory_type": memory_type,
            },
        )


class MemorySerializationError(MemoryError):
    """
    Raised when serialization/deserialization fails.
    """


class MemoryPermissionError(MemoryError):
    """
    Raised when access to a memory is denied.
    """


class MemoryConflictError(MemoryError):
    """
    Raised when concurrent updates conflict.
    """


class MemoryTimeoutError(MemoryError):
    """
    Raised when a backend operation exceeds the timeout.
    """