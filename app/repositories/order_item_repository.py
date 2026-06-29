from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.order_item import OrderItem
from app.repositories.base import Repository


class OrderItemRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = OrderItem

    def get_by_order_id(self, order_id: int) -> List[OrderItem]:
        return self.db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    def create(self, order_id: int, product_id: int, product_name: str, product_price: float, quantity: int) -> OrderItem:
        order_item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            product_name=product_name,
            product_price=product_price,
            quantity=quantity,
        )
        self.db.add(order_item)
        self.db.commit()
        self.db.refresh(order_item)
        return order_item

    def get_by_id(self, order_item_id: int) -> Optional[OrderItem]:
        return self.db.query(OrderItem).filter(OrderItem.id == order_item_id).first()

    def delete(self, order_item_id: int) -> bool:
        return super().delete(OrderItem, order_item_id)

    def update_quantity(self, order_item_id: int, quantity: int) -> Optional[OrderItem]:
        order_item = self.get_by_id(order_item_id)
        if order_item:
            order_item.quantity = quantity
            self.db.commit()
            self.db.refresh(order_item)
        return order_item

    def get_total_amount(self, order_id: int) -> float:
        order_items = self.get_by_order_id(order_id)
        return sum(item.product_price * item.quantity for item in order_items)
