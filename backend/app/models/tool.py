from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.models.base import Entity
class Tool(Entity):
    """
    AI Tool Registry.
    """

    __tablename__ = "tools"
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    version: Mapped[str] = mapped_column(
        String(50),
        default="1.0.0",
    )

    api_version: Mapped[str | None] = mapped_column(
        String(50),
    )


    permission: Mapped[str] = mapped_column(
        String(100),
        default="user",
    )

    requires_confirmation: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    sandboxed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    healthy: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    built_in: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    configuration: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    capabilities: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )

    supported_languages: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )
    usage_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    success_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    failure_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    average_runtime: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer,
        default=60,
    )

    max_retries: Mapped[int] = mapped_column(
        Integer,
        default=3,
    )
    @property
    def success_rate(self) -> float:

        total = self.success_count + self.failure_count

        if total == 0:
            return 0.0

        return (self.success_count / total) * 100
    @property
    def is_available(self) -> bool:

        return (
            self.enabled
            and self.healthy
        )
Index(
    "idx_tool_name",
    Tool.name,
)

Index(
    "idx_tool_category",
    Tool.category,
)

Index(
    "idx_tool_permission",
    Tool.permission,
)

Index(
    "idx_tool_enabled",
    Tool.enabled,
)

Index(
    "idx_tool_healthy",
    Tool.healthy,
)

Index(
    "idx_tool_builtin",
    Tool.built_in,
)