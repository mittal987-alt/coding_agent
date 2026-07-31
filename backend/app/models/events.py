from __future__ import annotations

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Entity


class Event(Entity):
    """
    Event store entry for system and AI events.
    """

    __tablename__ = "events"

    project_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    aggregate_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    event_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )
    payload: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    event_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        default=dict,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )
    processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    processing_node: Mapped[str | None] = mapped_column(
        String(100),
    )
    correlation_id: Mapped[str | None] = mapped_column(
        String(100),
    )

    causation_id: Mapped[str | None] = mapped_column(
        String(100),
    )

    workflow_id: Mapped[str | None] = mapped_column(
        String(100),
    )
    agent_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    tool_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    model_name: Mapped[str | None] = mapped_column(
        String(100),
    )


    user = relationship(
        "User",
    )

    project = relationship(
        "Project",
        back_populates="events",
    )

    @property
    def is_retryable(self) -> bool:
        return (
            not self.processed
            and self.retry_count < 5
        )

    @property
    def has_workflow(self) -> bool:
        return self.workflow_id is not None


Index(
    "idx_event_type",
    Event.event_type,
)

Index(
    "idx_event_project",
    Event.project_id,
)

Index(
    "idx_event_user",
    Event.user_id,
)

Index(
    "idx_event_aggregate",
    Event.aggregate_id,
)

Index(
    "idx_event_workflow",
    Event.workflow_id,
)

Index(
    "idx_event_processed",
    Event.processed,
)

Index(
    "idx_event_correlation",
    Event.correlation_id,
)