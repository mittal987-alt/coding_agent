# vector/__init__.py
"""
Vector Memory

Provides embedding storage and similarity search for
the AI Software Engineer.

Responsibilities:
- Store vector embeddings
- Similarity search
- Nearest-neighbor retrieval
- Embedding management
- Hybrid search integration
"""

from .faiss_store import FAISSVectorStore
from .manager import VectorMemoryManager
from .retrieval import VectorRetriever

__all__ = [
    "VectorMemoryManager",
    "VectorRetriever",
    "FAISSVectorStore",
]