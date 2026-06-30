from fastapi import Query
from pydantic import BaseModel, Field
from typing import List, Generic, Optional, TypeVar


T = TypeVar("T")


class PaginationParams:
    def __init__(
        self,
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, ge=1, le=100),
    ):
        self.skip = skip
        self.limit = limit


class PaginationMeta(BaseModel):
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    total_pages: int


class PaginationResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta
