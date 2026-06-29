from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.cart_item import CartItems
from app.repositories.base import Repository


class CartItemRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = CartItems

    def get_by_cart_and_product(self, cart_id: int, product_id: int) -> Optional[CartItems]:
        return self.db.query(CartItems).filter(CartItems.cart_id == cart_id, CartItems.product_id == product_id).first()

    def get_by_cart(self, cart_id: int) -> List[CartItems]:
        return self.db.query(CartItems).filter(CartItems.cart_id == cart_id).all()

    def create(self, cart_id: int, product_id: int, quantity: int = 1) -> CartItems:
        cart_item = CartItems(cart_id=cart_id, product_id=product_id, quantity=quantity)
        self.db.add(cart_item)
        self.db.commit()
        self.db.refresh(cart_item)
        return cart_item

    def update_quantity(self, cart_item_id: int, quantity: int) -> Optional[CartItems]:
        cart_item = self.get(CartItems, cart_item_id)
        if cart_item:
            cart_item.quantity = quantity
            self.db.commit()
            self.db.refresh(cart_item)
        return cart_item

    def delete(self, cart_item_id: int) -> bool:
        return super().delete(CartItems, cart_item_id)

    def delete_by_cart_and_product(self, cart_id: int, product_id: int) -> bool:
        cart_item = self.get_by_cart_and_product(cart_id, product_id)
        if cart_item:
            self.db.delete(cart_item)
            self.db.commit()
            return True
        return False

    def get_cart_items_count(self, cart_id: int) -> int:
        return self.db.query(CartItems).filter(CartItems.cart_id == cart_id).count()

    def get_total(self, cart_id: int) -> float:
        from app.models.product import Product
        result = (
            self.db.query(CartItems, Product.price)
            .join(Product, CartItems.product_id == Product.id)
            .filter(CartItems.cart_id == cart_id)
            .all()
        )
        return sum(item.quantity * price for item, price in result)
