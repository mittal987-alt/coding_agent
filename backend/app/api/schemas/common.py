#
from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field
T = TypeVar("T")
class BaseSchema(BaseModel):

    model_config = ConfigDict(

        from_attributes=True,

        populate_by_name=True,

        extra="ignore",

        validate_assignment=True,
    )
class TimestampSchema(BaseSchema):

    created_at: datetime | None = None

    updated_at: datetime | None = None
class IdentifierSchema(BaseSchema):

    id: str
class PaginationRequest(BaseSchema):

    page: int = Field(

        default=1,

        ge=1,
    )

    page_size: int = Field(

        default=20,

        ge=1,

        le=100,
    )

class PaginationMeta(BaseSchema):

    page: int

    page_size: int

    total: int

    pages: int

class PaginatedResponse(
    BaseSchema,
    Generic[T],
):

    items: list[T]

    pagination: PaginationMeta

class SuccessResponse(BaseSchema):

    success: bool = True

    message: str | None = None

class ApiResponse(
    BaseSchema,
    Generic[T],
):

    success: bool = True

    data: T
class HealthResponse(BaseSchema):

    status: str

    uptime: float

    version: str
class MessageResponse(BaseSchema):

    message: str
class DeleteResponse(BaseSchema):

    success: bool = True

class SearchRequest(BaseSchema):

    query: str = Field(

        min_length=1,

        max_length=1000,
    )

    limit: int = Field(

        default=10,

        ge=1,

        le=100,
    )
class SortRequest(BaseSchema):

    field: str

    descending: bool = False
class FilterRequest(BaseSchema):

    filters: dict[str, Any] = Field(
        default_factory=dict,
    )