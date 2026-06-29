from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.models.order import Order
from app.repositories.base import Repository


class OrderRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        return self.db.query(Order).filter(Order.id == order_id).first()

    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).filter(Order.user_id == user_id).offset(skip).limit(limit).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).offset(skip).limit(limit).all()

    def create(self, user_id: int, total_amount: float, **kwargs) -> Order:
        order = Order(user_id=user_id, total_amount=total_amount, **kwargs)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update(self, order_id: int, **kwargs) -> Optional[Order]:
        return super().update(Order, order_id, **kwargs)

    def delete(self, order_id: int) -> bool:
        return super().delete(Order, order_id)

    def count_by_status(self, user_id: int, status: str) -> int:
        return self.db.query(Order).filter(Order.user_id == user_id, Order.status == status).count()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.db.query(Order).filter(Order.status == status).offset(skip).limit(limit).all()

    def search(self, user_id: Optional[int] = None, status: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Order]:
        query = self.db.query(Order)
        if user_id:
            query = query.filter(Order.user_id == user_id)
        if status:
            query = query.filter(Order.status == status)
        if date_from:
            query = query.filter(Order.created_at >= date_from)
        if date_to:
            query = query.filter(Order.created_at <= date_to)
        return query.all()
