from __future__ import annotations

from sqlalchemy import (
    ForeignKey,
    Index,
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
class AuditLog(Entity):
    """
    Immutable audit log entry.
    """

    __tablename__ = "audit_logs"
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(100),
    )
    method: Mapped[str | None] = mapped_column(
        String(20),
    )

    endpoint: Mapped[str | None] = mapped_column(
        String(500),
    )

    status_code: Mapped[int | None] = mapped_column()
    ip_address: Mapped[str | None] = mapped_column(
        String(100),
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
    )
    model_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    tool_name: Mapped[str | None] = mapped_column(
        String(100),
    )

    execution_id: Mapped[str | None] = mapped_column(
        String(100),
    )
    audit_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSON,
        default=dict,
    )

    details: Mapped[str | None] = mapped_column(
        Text,
    )
    user = relationship(
        "User",
        back_populates="audits",
    )
    @property
    def is_success(self) -> bool:

        return (
            self.status_code is not None
            and 200 <= self.status_code < 300
        )

    @property
    def is_error(self) -> bool:

        return (
            self.status_code is not None
            and self.status_code >= 400
        )
Index(
    "idx_audit_user",
    AuditLog.user_id,
)

Index(
    "idx_audit_action",
    AuditLog.action,
)

Index(
    "idx_audit_resource_type",
    AuditLog.resource_type,
)

Index(
    "idx_audit_resource_id",
    AuditLog.resource_id,
)

Index(
    "idx_audit_tool",
    AuditLog.tool_name,
)

Index(
    "idx_audit_model",
    AuditLog.model_name,
)

Index(
    "idx_audit_status",
    AuditLog.status_code,
)