"""
Context Expander

Expands retrieved chunks using repository intelligence.

Expansion Sources

- Parent class
- Child methods
- Call graph
- Dependency graph
- Neighbor code
- Imports
"""

from __future__ import annotations

from collections import OrderedDict

from app.indexers.repository_index import RepositoryIndex
from app.retrieval.models import RetrievalResult


class ContextExpander:

    def __init__(
        self,
        repository: RepositoryIndex,
    ):

        self.repository = repository

    def expand(
        self,
        results: list[RetrievalResult],
        max_chunks: int = 30,
    ) -> list[RetrievalResult]:

        expanded = []

        for result in results:

            expanded.append(result)

            expanded.extend(
                self.expand_class(result)
            )

            expanded.extend(
                self.expand_calls(result)
            )

            expanded.extend(
                self.expand_callers(result)
            )

            expanded.extend(
                self.expand_imports(result)
            )

            expanded.extend(
                self.expand_neighbors(result)
            )

        expanded = self.remove_duplicates(
            expanded
        )

        return expanded[:max_chunks]

    def expand_class(
        self,
        result: RetrievalResult,
    ) -> list[RetrievalResult]:

        symbol = result.chunk.symbol

        if symbol is None:
            return []

        return self.repository.graph.class_context(
            symbol
        )

    def expand_calls(
        self,
        result: RetrievalResult,
    ) -> list[RetrievalResult]:

        symbol = result.chunk.symbol

        if symbol is None:
            return []

        return self.repository.graph.called_functions(
            symbol
        )

    def expand_callers(
        self,
        result: RetrievalResult,
    ) -> list[RetrievalResult]:

        symbol = result.chunk.symbol

        if symbol is None:
            return []

        return self.repository.graph.callers(
            symbol
        )

    def expand_imports(
        self,
        result: RetrievalResult,
    ) -> list[RetrievalResult]:

        return self.repository.graph.import_context(
            result.chunk.file
        )

    def expand_neighbors(
        self,
        result: RetrievalResult,
    ) -> list[RetrievalResult]:

        return self.repository.files.neighbor_chunks(
            result.chunk.file,
            result.chunk.start_line,
        )

    def remove_duplicates(
        self,
        results: list[RetrievalResult],
    ) -> list[RetrievalResult]:

        unique = OrderedDict()

        for result in results:

            unique[result.chunk.id] = result

        return list(unique.values())