from datetime import datetime, timezone
from typing import Optional, Any, Dict, TypeVar, Generic, List

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin:
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SoftDeleteMixin:
    is_deleted: bool = Field(default=False)
    deleted_at: Optional[datetime] = Field(default=None)


T = TypeVar("T", bound=BaseModel)


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginationResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta
