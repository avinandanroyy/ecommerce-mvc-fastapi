from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.models.product import Product
from app.utils.slugify import slugify


class ProductService:
    def __init__(self, db: Session):
        self.repo = ProductRepository(db)
        self.category_repo = CategoryRepository(db)

    def create(self, name: str, description: Optional[str], price: float, category_id: Optional[int] = None) -> Product:
        if category_id:
            category = self.category_repo.get_by_id(category_id)
            if not category:
                raise ValueError("Category not found")

        slug = slugify(name)
        existing = self.repo.get_by_slug(slug)
        if existing:
            raise ValueError("Product with this name already exists")

        product = self.repo.create(
            name=name,
            slug=slug,
            description=description,
            price=price,
            category_id=category_id,
            stock_quantity=0,
        )
        return product

    def get_by_id(self, product_id: int) -> Optional[Product]:
        product = self.repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        return product

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return self.repo.get_by_slug(slug)

    def update(self, product_id: int, **kwargs) -> Optional[Product]:
        product = self.get_by_id(product_id)
        return self.repo.update(product_id, **kwargs)

    def delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        return self.repo.delete(product_id)

    def soft_delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        return self.repo.soft_delete(product_id)

    def restore(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        return self.repo.restore(product_id)

    def list_all(self, skip: int = 0, limit: int = 100, category_id: Optional[int] = None) -> List[Product]:
        return self.repo.list_all(skip, limit, category_id)

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.repo.search(query, skip, limit)

    def get_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.repo.get_by_category(category_id, skip, limit)

    def list_all_with_pagination(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> dict:
        products = self.repo.list_all_with_details(skip, limit, sort_by, sort_order, category_id, min_price, max_price)
        total = self.repo.get_total_count(category_id)
        return {
            "data": products,
            "meta": {
                "total": total,
                "page": skip // limit + 1,
                "page_size": limit,
                "total_pages": (total + limit - 1) // limit,
            },
        }

    def update_stock(self, product_id: int, quantity_change: int) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product.stock_quantity + quantity_change < 0:
            raise ValueError("Insufficient stock")
        return self.repo.update_stock(product_id, quantity_change)

    def get_top_rated_products(self, limit: int = 5) -> List[Product]:
        return self.repo.get_top_rated_products(limit)

    def get_by_ids(self, product_ids: List[int]) -> List[Product]:
        return self.repo.get_by_ids(product_ids)
