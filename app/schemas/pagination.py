from pydantic import BaseModel, Field
from typing import List, Generic, TypeVar


T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    total_pages: int


class PaginationResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta
