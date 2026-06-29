from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=255)


class CategoryResponse(CategoryBase):
    id: int
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: str
