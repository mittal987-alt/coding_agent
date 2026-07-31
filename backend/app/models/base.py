# Compatibility shim — re-exports from base_model so that
# `from app.models.base import Entity` continues to work.
from app.models.base_model import (
    Base,
    BaseModel,
    Entity,
    TimestampMixin,
    UUIDMixin,
    SoftDeleteMixin,
    AuditMixin,
    VersionMixin,
    metadata,
)

__all__ = [
    "Base",
    "BaseModel",
    "Entity",
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    "AuditMixin",
    "VersionMixin",
    "metadata",
]
