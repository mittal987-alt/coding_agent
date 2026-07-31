from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Entity

class Metric(Entity):
    """
    System metric entry.
    """

    __tablename__ = "metrics"

    user_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    project_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    metric_type: Mapped[str] = mapped_column(
        String(50),
        default="counter",
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
    )
    category: Mapped[str] = mapped_column(
        String(100),
        default="system",
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
    )

    provider: Mapped[str | None] = mapped_column(
        String(100),
    )
    tags: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    metric_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )
    model_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    tool_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    workflow_id: Mapped[str | None] = mapped_column(
        String(100),
    )
    user = relationship(
        "User",
    )

    project = relationship(
        "Project",
    )
    @property
    def is_cost_metric(self) -> bool:
        return self.category == "cost"

    @property
    def is_latency_metric(self) -> bool:
        return self.category == "latency"

    @property
    def is_token_metric(self) -> bool:
        return self.category == "tokens"

    @property
    def is_error_metric(self) -> bool:
        return self.category == "errors"
Index(
    "idx_metric_name",
    Metric.name,
)

Index(
    "idx_metric_type",
    Metric.metric_type,
)

Index(
    "idx_metric_category",
    Metric.category,
)

Index(
    "idx_metric_provider",
    Metric.provider,
)

Index(
    "idx_metric_model",
    Metric.model_name,
)

Index(
    "idx_metric_tool",
    Metric.tool_name,
)

Index(
    "idx_metric_user",
    Metric.user_id,
)

Index(
    "idx_metric_project",
    Metric.project_id,
)