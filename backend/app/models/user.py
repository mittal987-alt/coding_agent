from __future__ import annotations

from sqlalchemy import (
    Boolean,
    Index,
    Integer,
    String,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Entity

class User(Entity):
    """
    Application user.
    """

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(

        String(255),

        unique=True,

        nullable=False,
    )

    username: Mapped[str] = mapped_column(

        String(100),

        unique=True,

        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(

        String(512),

        nullable=False,
    )   
    full_name: Mapped[str] = mapped_column(

        String(255),

        nullable=False,
    )

    avatar: Mapped[str | None] = mapped_column(

        String(1024),

        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(

        String(1000),

        nullable=True,
    )
    role: Mapped[str] = mapped_column(

        String(50),

        default="user",

        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(

        Boolean,

        default=True,
    )

    email_verified: Mapped[bool] = mapped_column(

        Boolean,

        default=False,
    )

    is_superuser: Mapped[bool] = mapped_column(

        Boolean,

        default=False,
    )
    refresh_token: Mapped[str | None] = mapped_column(

        String(512),

        nullable=True,
    )

    failed_login_attempts: Mapped[int] = mapped_column(

        Integer,

        default=0,
    )

    last_login_ip: Mapped[str | None] = mapped_column(

        String(100),

        nullable=True,
    )
    workspaces = relationship(

        "Workspace",

        back_populates="owner",
    )

    chats = relationship(

        "Chat",

        back_populates="user",
    )

    memories = relationship(

        "Memory",

        back_populates="user",
    )

    audits = relationship(

        "AuditLog",

        back_populates="user",
    )
    @property
    def display_name(self) -> str:

        return self.full_name or self.username
# ----------------------------------------------------------
# Indexes
# ----------------------------------------------------------

Index("idx_users_email", User.email)
Index("idx_users_username", User.username)
Index("idx_users_role", User.role)
Index("idx_users_active", User.is_active)