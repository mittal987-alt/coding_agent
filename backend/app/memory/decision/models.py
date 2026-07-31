# decision/models.py
from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------


class DecisionType(str, Enum):
    """
    Category of decision.
    """

    ARCHITECTURE = "architecture"
    PLANNING = "planning"
    TOOL = "tool"
    FRAMEWORK = "framework"
    DATABASE = "database"
    ALGORITHM = "algorithm"
    SECURITY = "security"
    PERFORMANCE = "performance"
    REFACTORING = "refactoring"
    DEPLOYMENT = "deployment"
    TESTING = "testing"
    OTHER = "other"


class DecisionStatus(str, Enum):
    """
    Lifecycle of a decision.
    """

    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"


class DecisionOutcome(str, Enum):
    """
    Outcome after implementation.
    """

    UNKNOWN = "unknown"
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    ROLLED_BACK = "rolled_back"


# ----------------------------------------------------------------------
# Supporting Models
# ----------------------------------------------------------------------


class DecisionAlternative(BaseModel):
    """
    Alternative considered during reasoning.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    title: str

    description: str = ""

    pros: list[str] = Field(default_factory=list)

    cons: list[str] = Field(default_factory=list)

    selected: bool = False


class DecisionEvidence(BaseModel):
    """
    Evidence supporting the decision.
    """

    source: str

    description: str

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )


# ----------------------------------------------------------------------
# Main Decision Model
# ----------------------------------------------------------------------


class DecisionMemory(BaseModel):
    """
    Stores an AI reasoning decision.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    project_id: str | None = None

    conversation_id: str | None = None

    episode_id: str | None = None

    title: str

    description: str

    decision_type: DecisionType

    status: DecisionStatus = DecisionStatus.ACCEPTED

    outcome: DecisionOutcome = DecisionOutcome.UNKNOWN

    reasoning: str = ""

    rationale: str = ""

    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
    )

    alternatives: list[DecisionAlternative] = Field(
        default_factory=list
    )

    evidence: list[DecisionEvidence] = Field(
        default_factory=list
    )

    related_files: list[str] = Field(default_factory=list)

    related_memories: list[str] = Field(default_factory=list)

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


class DecisionStatistics(BaseModel):
    """
    Decision analytics.
    """

    total_decisions: int

    accepted: int

    rejected: int

    superseded: int

    successful: int

    failed: int

    average_confidence: float

    last_updated: datetime