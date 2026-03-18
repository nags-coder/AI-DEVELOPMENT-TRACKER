"""Common response envelope schemas used across endpoints."""

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Metadata about a paginated response."""

    page: int
    per_page: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    """Standard paginated envelope: { data: [...], meta: {...} }."""

    data: list[T]
    meta: PaginationMeta
