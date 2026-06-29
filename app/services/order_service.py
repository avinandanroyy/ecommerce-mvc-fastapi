from typing import Optional, List
from sqlalchemy.orm import Session
from contextlib import contextmanager

from app.repositories.order_repository import OrderRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.models.order import Order
from app.models.order_item import OrderItem


class OrderService:
    def __init__(self, db: Session):
        self.order_repo = OrderRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.product_repo = ProductRepository(db)
        self.cart_repo = CartRepository(db)
        self.cart_item_repo = CartItemRepository(db)

    @contextmanager
    def transaction(self):
        try:
            yield
            self.order_repo.db.commit()
        except Exception as e:
            self.order_repo.db.rollback()
            raise e

    def create_order(self, user_id: int, shipping_address: Optional[str] = None, payment_method: Optional[str] = None) -> Order:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            raise ValueError("Cart is empty")

        cart_items = self.cart_item_repo.get_by_cart(cart.id)
        if not cart_items:
            raise ValueError("Cart is empty")

        total_amount = 0.0
        order = self.order_repo.create(user_id, 0.0, shipping_address=shipping_address, payment_method=payment_method, status="pending")

        try:
            for item in cart_items:
                product = self.product_repo.get_by_id(item.product_id)
                if not product:
                    raise ValueError(f"Product {item.product_id} not found")
                if item.quantity > product.stock_quantity:
                    raise ValueError(f"Insufficient stock for product {product.name}")

                self.order_item_repo.create(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_price=product.price,
                    quantity=item.quantity,
                )

                total_amount += item.quantity * product.price
                self.product_repo.update_stock(product.id, -item.quantity)

            order.total_amount = total_amount
            order.status = "confirmed"
            self.order_repo.db.commit()
            self.order_repo.db.refresh(order)

            self.cart_item_repo.db.query(CartItems).filter(CartItems.cart_id == cart.id).delete()
            self.cart_item_repo.db.commit()

        except Exception as e:
            self.order_repo.db.rollback()
            raise e

        return order

    def get_order(self, order_id: int) -> Optional[Order]:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        return order

    def get_orders_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.order_repo.get_by_user_id(user_id, skip, limit)

    def cancel_order(self, order_id: int, user_id: int) -> bool:
        order = self.get_order(order_id)
        if order.user_id != user_id:
            raise ValueError("You can only cancel your own orders")
        if order.status in ["cancelled", "delivered"]:
            raise ValueError("Cannot cancel order in this status")

        order.status = "cancelled"
        self.order_repo.db.commit()

        for item in order.items:
            self.product_repo.update_stock(item.product_id, item.quantity)

        return True

    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        order = self.get_order(order_id)
        order.status = status
        self.order_repo.db.commit()
        self.order_repo.db.refresh(order)
        return order

    def get_order_history(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return self.order_repo.get_by_user_id(user_id, skip, limit)

    def get_order_items(self, order_id: int) -> List[OrderItem]:
        order = self.get_order(order_id)
        return self.order_item_repo.get_by_order_id(order_id)
