"""
Models for AI code review.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ReviewSeverity(str, Enum):

    INFO = "info"

    WARNING = "warning"

    ERROR = "error"


class ReviewIssue(BaseModel):

    file: str

    line: int | None = None

    severity: ReviewSeverity

    message: str

    recommendation: str


class ReviewResult(BaseModel):

    approved: bool

    summary: str

    issues: list[ReviewIssue]