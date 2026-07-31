from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)
metadata = MetaData(

    naming_convention={

        "ix": "ix_%(column_0_label)s",

        "uq": "uq_%(table_name)s_%(column_0_name)s",

        "ck": "ck_%(table_name)s_%(constraint_name)s",

        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",

        "pk": "pk_%(table_name)s",
    }
)
class Base(DeclarativeBase):

    metadata = metadata
class TimestampMixin:

    created_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        default=lambda: datetime.now(
            UTC,
        ),

        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(

        DateTime(timezone=True),

        default=lambda: datetime.now(
            UTC,
        ),

        onupdate=lambda: datetime.now(
            UTC,
        ),

        nullable=False,
    )
class UUIDMixin:

    id: Mapped[uuid.UUID] = mapped_column(

        UUID(as_uuid=True),

        primary_key=True,

        default=uuid.uuid4,
    )
class BaseModel(

    Base,

    UUIDMixin,

    TimestampMixin,
):

    __abstract__ = True
class SoftDeleteMixin:

    deleted_at: Mapped[datetime | None] = mapped_column(

        DateTime(timezone=True),

        nullable=True,
    )

    @property
    def is_deleted(self) -> bool:

        return self.deleted_at is not None  
class AuditMixin:

    created_by: Mapped[str | None] = mapped_column(
        nullable=True,
    )

    updated_by: Mapped[str | None] = mapped_column(
        nullable=True,
    )
class VersionMixin:

    version: Mapped[int] = mapped_column(

        default=1,

        nullable=False,
    )
class Entity(

    BaseModel,

    SoftDeleteMixin,

    AuditMixin,

    VersionMixin,
):

    __abstract__ = True