from typing import Optional, List

from sqlalchemy.orm import Session

from app.repositories.category_repository import CategoryRepository
from app.models.category import Category


class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def create(self, name: str, description: Optional[str] = None) -> Category:
        existing_category = self.repo.get_by_name(name)
        if existing_category:
            raise ValueError("Category with this name already exists")
        return self.repo.create(name=name, description=description)

    def get_by_id(self, category_id: int) -> Optional[Category]:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        return category

    def update(self, category_id: int, name: Optional[str] = None, description: Optional[str] = None) -> Optional[Category]:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        if name:
            existing = self.repo.get_by_name(name)
            if existing and existing.id != category_id:
                raise ValueError("Category with this name already exists")
        return self.repo.update(category_id, name=name, description=description)

    def delete(self, category_id: int) -> bool:
        category = self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        return self.repo.delete(category_id)

    def list_all_active(self, skip: int = 0, limit: int = 100) -> List[Category]:
        return self.repo.list_all_active(skip, limit)

    def get_category_with_product_count(self, category_id: int) -> dict:
        category = self.get_by_id(category_id)
        product_count = self.repo.count_products(category_id)
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "product_count": product_count,
        }

    def search_categories(self, query: str) -> List[Category]:
        return self.repo.db.query(Category).filter(Category.name.ilike(f"%{query}%")).all()
