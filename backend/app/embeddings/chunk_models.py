"""
CodeChunk — Atomic unit of indexed code for embedding and retrieval.

Each chunk represents a logically complete code segment (function, class,
method, or file block) extracted by the Tree-sitter AST indexer.
"""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field


class CodeChunk(BaseModel):
    """
    A single indexed code segment stored in the vector database.

    Fields:
        id:           Unique chunk identifier (UUID4 string).
        workspace_id: ID of the workspace this chunk belongs to.
        file:         Relative file path within the workspace.
        language:     Programming language identifier (e.g. 'python', 'typescript').
        symbol:       Name of the function/class/method this chunk represents, if any.
        kind:         AST node kind: 'class', 'function', 'method', or None for raw blocks.
        start_line:   1-indexed starting line of the chunk within the file.
        end_line:     1-indexed ending line (inclusive).
        content:      Raw source code text of the chunk.
        metadata:     Arbitrary key-value metadata (e.g. docstring, decorators, imports).
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique chunk identifier (UUID4). Auto-generated if not provided.",
    )

    workspace_id: int = Field(
        ...,
        description="ID of the owning workspace / repository.",
    )

    file: str = Field(
        ...,
        description="Relative file path within the workspace (e.g. 'app/api/chat.py').",
    )

    language: str = Field(
        default="",
        description="Programming language identifier (e.g. 'python', 'typescript').",
    )

    symbol: Optional[str] = Field(
        default=None,
        description="AST symbol name (function/class/method name) this chunk belongs to.",
    )

    kind: Optional[str] = Field(
        default=None,
        description="AST node kind: 'class', 'function', 'method', or None for file-level blocks.",
    )

    start_line: int = Field(
        default=1,
        description="1-indexed starting line of this chunk within the file.",
    )

    end_line: int = Field(
        default=1,
        description="1-indexed ending line (inclusive) of this chunk within the file.",
    )

    content: str = Field(
        default="",
        description="Raw source code text of this chunk.",
    )

    metadata: dict = Field(
        default_factory=dict,
        description="Arbitrary key-value metadata (docstring, decorators, call graph edges, etc.).",
    )

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def file_path(self) -> str:
        """Alias for `file` — used by ranker and retrieval modules."""
        return self.file

    @property
    def line_count(self) -> int:
        """Number of source lines in this chunk."""
        return max(0, self.end_line - self.start_line + 1)