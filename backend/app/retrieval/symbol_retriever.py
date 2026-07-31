"""
Symbol Retriever

Performs exact lookup on repository symbols.

Examples:
- UserService
- login
- JWTService.generate
- Database
"""

from __future__ import annotations

from typing import List

from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import (
    RetrievalResult,
    RetrievalSource,
)


class SymbolRetriever:

    """
    Retrieves symbols directly from SymbolIndex.

    Supports:

    • Classes
    • Functions
    • Methods
    • Variables
    • Interfaces
    • Enums
    """

    def __init__(
        self,
        repository: RepositoryIndex,
    ) -> None:

        self.repository = repository

    def retrieve(
        self,
        query: str,
    ) -> List[RetrievalResult]:

        query = query.strip()

        results = []

        symbol_index = self.repository.symbols

        matches = symbol_index.find(query)

        for symbol in matches:

            chunk = self.repository.embeddings.chunk_for_symbol(
                symbol.id
            )

            if chunk is None:
                continue

            results.append(

                RetrievalResult(

                    chunk=chunk,

                    score=1.0,

                    source=RetrievalSource.SYMBOL,

                    metadata={

                        "symbol": symbol.name,

                        "kind": symbol.kind.value,

                    },

                )

            )

        return results

    def find_class(
        self,
        name: str,
    ) -> List[RetrievalResult]:

        return self._find_by_kind(
            name,
            "class",
        )

    def find_function(
        self,
        name: str,
    ) -> List[RetrievalResult]:

        return self._find_by_kind(
            name,
            "function",
        )

    def find_method(
        self,
        name: str,
    ) -> List[RetrievalResult]:

        return self._find_by_kind(
            name,
            "method",
        )

    def find_variable(
        self,
        name: str,
    ) -> List[RetrievalResult]:

        return self._find_by_kind(
            name,
            "variable",
        )

    def _find_by_kind(
        self,
        name: str,
        kind: str,
    ) -> List[RetrievalResult]:

        results = []

        symbols = self.repository.symbols.find(name)

        for symbol in symbols:

            if symbol.kind.value != kind:
                continue

            chunk = self.repository.embeddings.chunk_for_symbol(
                symbol.id
            )

            if chunk is None:
                continue

            results.append(

                RetrievalResult(

                    chunk=chunk,

                    score=1.0,

                    source=RetrievalSource.SYMBOL,

                    metadata={
                        "kind": kind,
                    },

                )

            )

        return results