from __future__ import annotations

from enum import Enum
from pydantic import BaseModel

from app.embeddings.chunk_models import CodeChunk


class RetrievalSource(str, Enum):

    VECTOR = "vector"

    SYMBOL = "symbol"

    GRAPH = "graph"


class RetrievalResult(BaseModel):

    chunk: CodeChunk

    score: float

    source: RetrievalSource

    metadata: dict = {}


class RetrievalResponse(BaseModel):

    query: str

    results: list[RetrievalResult]