"""
Context Builder

Builds the final LLM context using:

- Retrieved chunks
- Symbol graph
- Dependency graph
- Call graph
- Neighbor expansion
- Token budget
"""

from __future__ import annotations

from collections import OrderedDict
from typing import List

from app.embeddings.chunk_models import CodeChunk
from app.indexers.repository_index import RepositoryIndex


class ContextBuilder:

    """
    Builds optimized context for the LLM.

    Pipeline

    Retrieved Chunks
            │
            ▼
    Expand Symbols
            │
            ▼
    Expand Call Graph
            │
            ▼
    Expand Imports
            │
            ▼
    Expand Neighbor Chunks
            │
            ▼
    Remove Duplicates
            │
            ▼
    Token Budget
            │
            ▼
    Final Prompt
    """

    def __init__(self, repository: RepositoryIndex):

        self.repository = repository

    def build(
        self,
        query: str,
        chunks: List[CodeChunk],
        max_tokens: int = 12000,
    ) -> str:

        expanded = []

        for chunk in chunks:

            expanded.extend(
                self.expand(chunk)
            )

        expanded = self.remove_duplicates(
            expanded
        )

        expanded = self.apply_budget(
            expanded,
            max_tokens,
        )

        return self.render(
            query,
            expanded,
        )

    def expand(
        self,
        chunk: CodeChunk,
    ) -> List[CodeChunk]:

        context = [chunk]

        context.extend(
            self.class_context(chunk)
        )

        context.extend(
            self.call_context(chunk)
        )

        context.extend(
            self.import_context(chunk)
        )

        context.extend(
            self.neighbor_context(chunk)
        )

        return context

    def remove_duplicates(
        self,
        chunks: List[CodeChunk],
    ) -> List[CodeChunk]:

        unique = OrderedDict()

        for chunk in chunks:

            unique[chunk.id] = chunk

        return list(unique.values())

    def apply_budget(
        self,
        chunks: List[CodeChunk],
        max_tokens: int,
    ) -> List[CodeChunk]:

        result = []

        used = 0

        for chunk in chunks:

            estimate = len(chunk.content) // 4

            if used + estimate > max_tokens:
                break

            result.append(chunk)

            used += estimate

        return result

    def render(
        self,
        query: str,
        chunks: List[CodeChunk],
    ) -> str:

        prompt = []

        prompt.append(
            "### USER QUESTION"
        )

        prompt.append(query)

        prompt.append("")

        prompt.append(
            "### REPOSITORY CONTEXT"
        )

        for chunk in chunks:

            prompt.append(
                f"\nFILE: {chunk.file}"
            )

            prompt.append(
                f"SYMBOL: {chunk.symbol}"
            )

            prompt.append(
                f"LINES: {chunk.start_line}-{chunk.end_line}"
            )

            prompt.append("```")

            prompt.append(
                chunk.content
            )

            prompt.append("```")

        return "\n".join(prompt)