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
class Model(Entity):
    """
    AI Model Registry.
    """

    __tablename__ = "models"
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
    )
    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    supports_chat: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    supports_functions: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    supports_vision: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    supports_audio: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    supports_embeddings: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    supports_streaming: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )
    context_window: Mapped[int] = mapped_column(
        Integer,
        default=8192,
    )

    max_output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=4096,
    )

    requests_per_minute: Mapped[int | None] = mapped_column(
        Integer,
    )

    tokens_per_minute: Mapped[int | None] = mapped_column(
        Integer,
    )
    input_price: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    output_price: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="USD",
    )
    version: Mapped[str | None] = mapped_column(
        String(50),
    )

    endpoint: Mapped[str | None] = mapped_column(
        String(1000),
    )

    configuration: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    capabilities: Mapped[list] = mapped_column(
        JSON,
        default=list,
    )
    total_requests: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    average_latency_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    @property
    def supports_multimodal(self) -> bool:
        return (
            self.supports_vision
            or self.supports_audio
        )

    @property
    def is_healthy(self) -> bool:
        return (
            self.available
            and self.enabled
        )
Index(
    "idx_models_name",
    Model.name,
)

Index(
    "idx_models_provider",
    Model.provider,
)

Index(
    "idx_models_default",
    Model.is_default,
)

Index(
    "idx_models_available",
    Model.available,
)

Index(
    "idx_models_enabled",
    Model.enabled,
)

Index(
    "idx_models_chat",
    Model.supports_chat,
)

Index(
    "idx_models_vision",
    Model.supports_vision,
)

Index(
    "idx_models_functions",
    Model.supports_functions,
)