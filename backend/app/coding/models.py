"""
Models representing AI-generated code edits.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class EditType(str, Enum):

    CREATE = "create"

    MODIFY = "modify"

    DELETE = "delete"


class FileEdit(BaseModel):

    path: str

    edit_type: EditType

    content: str

    explanation: str


class CodingResult(BaseModel):

    summary: str

    edits: list[FileEdit]