from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime


class ReviewBase(BaseModel):
    rating: float = Field(..., gt=0, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)

    @field_validator("rating")
    @classmethod
    def rating_must_be_between(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, gt=0, le=5)
    review_text: Optional[str] = Field(None, max_length=1000)


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: float
    review_text: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str]
    rating: float
    review_text: Optional[str]
    created_at: datetime


class ReviewListWithPagination(BaseModel):
    data: List[ReviewListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
