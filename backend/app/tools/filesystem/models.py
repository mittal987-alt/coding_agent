from __future__ import annotations

from enum import Enum

from pathlib import Path

from pydantic import BaseModel


class FileOperation(str, Enum):

    READ = "read"

    WRITE = "write"

    APPEND = "append"

    DELETE = "delete"

    MOVE = "move"

    COPY = "copy"

    LIST = "list"

    SEARCH = "search"

    METADATA = "metadata"


class FileInfo(BaseModel):

    path: str

    size: int

    is_file: bool

    is_directory: bool

    modified_time: float


class FileSearchResult(BaseModel):

    path: str

    line: int

    content: str