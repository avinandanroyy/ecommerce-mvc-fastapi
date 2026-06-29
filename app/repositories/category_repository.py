from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.category import Category
from app.repositories.base import Repository


class CategoryRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Category

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name == name).first()

    def get_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def create(self, **kwargs) -> Category:
        return super().create(Category, **kwargs)

    def update(self, category_id: int, **kwargs) -> Optional[Category]:
        return super().update(Category, category_id, **kwargs)

    def delete(self, category_id: int) -> bool:
        return super().delete(Category, category_id)

    def list_all_active(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.db.query(Category).filter(Category.is_active == 1).offset(skip).limit(limit).all()

    def count_products(self, category_id: int) -> int:
        from app.models.product import Product
        return self.db.query(Product).filter(Product.category_id == category_id).count()
