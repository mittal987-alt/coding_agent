from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------


class LearningCategory(str, Enum):
    """
    Category of learned knowledge.
    """

    EXECUTION = "execution"
    DEBUGGING = "debugging"
    PLANNING = "planning"
    CODING = "coding"
    TESTING = "testing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    ARCHITECTURE = "architecture"
    TOOL_USAGE = "tool_usage"
    USER_PREFERENCE = "user_preference"
    CODE_REVIEW = "code_review"
    OTHER = "other"


class LearningSource(str, Enum):
    """
    Source of learning.
    """

    EXECUTION = "execution"
    USER = "user"
    TOOL = "tool"
    AGENT = "agent"
    REVIEW = "review"
    BENCHMARK = "benchmark"
    SYSTEM = "system"


class LearningOutcome(str, Enum):
    """
    Result of applying learned knowledge.
    """

    UNKNOWN = "unknown"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    IMPROVED = "improved"


class FeedbackType(str, Enum):
    """
    Type of feedback received.
    """

    POSITIVE = "positive"
    NEGATIVE = "negative"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"


# ----------------------------------------------------------------------
# Supporting Models
# ----------------------------------------------------------------------


class LearningFeedback(BaseModel):
    """
    User or system feedback.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    feedback_type: FeedbackType

    message: str

    score: float = Field(
        default=1.0,
        ge=-1.0,
        le=1.0,
    )

    source: LearningSource

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class LearningPattern(BaseModel):
    """
    Reusable pattern extracted from experience.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    trigger: str

    recommendation: str

    examples: list[str] = Field(default_factory=list)


# ----------------------------------------------------------------------
# Main Model
# ----------------------------------------------------------------------


class LearningMemory(BaseModel):
    """
    Long-term learned knowledge.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str

    category: LearningCategory

    source: LearningSource

    outcome: LearningOutcome = LearningOutcome.UNKNOWN

    lesson: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    usage_count: int = 0

    success_count: int = 0

    failure_count: int = 0

    pattern: LearningPattern | None = None

    feedback: list[LearningFeedback] = Field(
        default_factory=list
    )

    project_ids: list[str] = Field(default_factory=list)

    related_files: list[str] = Field(default_factory=list)

    related_decisions: list[str] = Field(default_factory=list)

    tags: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


# ----------------------------------------------------------------------
# Statistics
# ----------------------------------------------------------------------


class LearningStatistics(BaseModel):
    """
    Learning analytics.
    """

    total_lessons: int

    successful_patterns: int

    failed_patterns: int

    average_confidence: float

    total_feedback: int

    total_usage: int

    last_updated: datetime