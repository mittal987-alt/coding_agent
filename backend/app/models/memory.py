from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Float,
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
class Memory(Entity):
    """
    Long-term AI memory.
    """

    __tablename__ = "memories"
    user_id: Mapped[str] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    project_id: Mapped[str | None] = mapped_column(
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
    )
    embedding: Mapped[list[float] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
    )

    embedding_dimensions: Mapped[int | None] = mapped_column(
        Integer,
    )
    importance: Mapped[float] = mapped_column(
        Float,
        default=0.5,
    )

    access_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    last_access_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )
    memory_type: Mapped[str] = mapped_column(
        String(50),
        default="general",
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
    )

    tags: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )
    archived: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    memory_metadata: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )
    user = relationship(
        "User",
        back_populates="memories",
    )

    project = relationship(
        "Project",
        back_populates="memories",
    )


    @property
    def has_embedding(self) -> bool:
        return self.embedding is not None

    @property
    def is_searchable(self) -> bool:
        return (
            not self.archived
            and self.embedding is not None
        )
Index(
    "idx_memory_user",
    Memory.user_id,
)

Index(
    "idx_memory_project",
    Memory.project_id,
)

Index(
    "idx_memory_type",
    Memory.memory_type,
)

Index(
    "idx_memory_category",
    Memory.category,
)

Index(
    "idx_memory_importance",
    Memory.importance,
)

Index(
    "idx_memory_archived",
    Memory.archived,
)