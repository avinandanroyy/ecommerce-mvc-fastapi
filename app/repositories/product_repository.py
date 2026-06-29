from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc, asc

from app.models.product import Product
from app.repositories.base import Repository


class ProductRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Product

    def get_by_slug(self, slug: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.slug == slug).first()

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def create(self, **kwargs) -> Product:
        return super().create(Product, **kwargs)

    def update(self, product_id: int, **kwargs) -> Optional[Product]:
        return super().update(Product, product_id, **kwargs)

    def delete(self, product_id: int) -> bool:
        return super().delete(Product, product_id)

    def list_all(
        self, skip: int = 0, limit: int = 100, category_id: Optional[int] = None, is_active: bool = True
    ) -> List[Product]:
        query = self.db.query(Product)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if is_active:
            query = query.filter(Product.is_active == 1, Product.is_deleted == False)
        return query.offset(skip).limit(limit).all()

    def search(self, query_str: str, skip: int = 0, limit: int = 100) -> List[Product]:
        return (
            self.db.query(Product)
            .filter(
                or_(
                    Product.name.ilike(f"%{query_str}%"),
                    Product.description.ilike(f"%{query_str}%"),
                )
            )
            .filter(Product.is_active == 1, Product.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(self, category_id: int, skip: int = 0, limit: int = 100) -> List[Product]:
        return (
            self.db.query(Product)
            .filter(Product.category_id == category_id, Product.is_active == 1, Product.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_all_with_details(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Product]:
        query = self.db.query(Product).filter(Product.is_active == 1, Product.is_deleted == False)

        if category_id:
            query = query.filter(Product.category_id == category_id)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        sort_column = getattr(Product, sort_by, Product.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        return query.offset(skip).limit(limit).all()

    def get_total_count(self, category_id: Optional[int] = None) -> int:
        query = self.db.query(Product).filter(Product.is_active == 1, Product.is_deleted == False)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        return query.count()

    def get_top_rated_products(self, limit: int = 5) -> List[Product]:
        from app.models.review import Review
        return (
            self.db.query(Product)
            .join(Review, Product.id == Review.product_id)
            .filter(Product.is_active == 1, Product.is_deleted == False)
            .group_by(Product.id)
            .order_by(func.avg(Review.rating).desc())
            .limit(limit)
            .all()
        )

    def get_by_ids(self, product_ids: List[int]) -> List[Product]:
        return self.db.query(Product).filter(Product.id.in_(product_ids), Product.is_active == 1).all()

    def update_stock(self, product_id: int, quantity_change: int) -> Optional[Product]:
        product = self.get_by_id(product_id)
        if product:
            product.stock_quantity = max(0, product.stock_quantity + quantity_change)
            self.db.commit()
            self.db.refresh(product)
        return product

    def soft_delete(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        if product:
            product.is_deleted = True
            self.db.commit()
            return True
        return False

    def restore(self, product_id: int) -> bool:
        product = self.get_by_id(product_id)
        if product:
            product.is_deleted = False
            self.db.commit()
            return True
        return False
