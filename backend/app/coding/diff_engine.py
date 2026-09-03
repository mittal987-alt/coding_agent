"""
Unified Line-Diff Patch Engine for enterprise AI code generation.
Reduces token costs and latency by generating line-level diff hunks rather than full-file overwrites.
"""

from __future__ import annotations

import difflib
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class EditType(str, Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"


class LineHunk(BaseModel):
    """Represents a single contiguous block of line edits within a file."""
    start_line: int = Field(..., description="1-indexed starting line number of the target block")
    end_line: int = Field(..., description="1-indexed ending line number of the target block")
    target_content: str = Field(..., description="Exact target lines to be replaced")
    replacement_content: str = Field(..., description="Replacement lines to insert")


class StructuredPatch(BaseModel):
    """Represents a line-diff patch applied to a file."""
    file_path: str = Field(..., description="Relative path of target file")
    edit_type: EditType = Field(default=EditType.MODIFY, description="Type of edit action")
    hunks: List[LineHunk] = Field(default_factory=list, description="List of line-diff hunks")
    full_content: Optional[str] = Field(default=None, description="Full content for newly created files")
    explanation: str = Field(default="", description="Reasoning for this patch")


class PatchEngineResult(BaseModel):
    """Result of applying one or more structured patches."""
    success: bool
    summary: str
    applied_patches: List[StructuredPatch] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class LineDiffEngine:
    """Engine for generating, parsing, and applying line-level diff patches."""

    @staticmethod
    def apply_patch(original_content: str, patch: StructuredPatch) -> str:
        """
        Applies a structured patch containing line hunks to original file content.
        """
        if patch.edit_type == EditType.CREATE:
            return patch.full_content or ""

        if patch.edit_type == EditType.DELETE:
            return ""

        if not patch.hunks:
            if patch.full_content is not None:
                return patch.full_content
            return original_content

        lines = original_content.splitlines(keepends=True)
        # Process hunks in reverse order (bottom to top) to preserve line indices
        sorted_hunks = sorted(patch.hunks, key=lambda h: h.start_line, reverse=True)

        for hunk in sorted_hunks:
            start_idx = max(0, hunk.start_line - 1)
            end_idx = min(len(lines), hunk.end_line)

            # Target lines replacement
            rep_lines = hunk.replacement_content.splitlines(keepends=True)
            if not hunk.replacement_content.endswith("\n") and rep_lines and original_content.endswith("\n"):
                rep_lines[-1] = rep_lines[-1] + "\n"

            lines[start_idx:end_idx] = rep_lines

        return "".join(lines)

    @staticmethod
    def generate_unified_diff(original_content: str, modified_content: str, file_path: str = "file") -> str:
        """
        Generates a standard unified git diff format string between original and modified content.
        """
        orig_lines = original_content.splitlines(keepends=True)
        mod_lines = modified_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            orig_lines,
            mod_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="\n"
        )
        return "".join(diff)
