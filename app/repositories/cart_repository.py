from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.cart import Cart
from app.repositories.base import Repository


class CartRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Cart

    def get_by_user_id(self, user_id: int) -> Optional[Cart]:
        return self.db.query(Cart).filter(Cart.user_id == user_id).first()

    def create_for_user(self, user_id: int) -> Cart:
        from app.models.cart import Cart
        cart = Cart(user_id=user_id)
        self.db.add(cart)
        self.db.commit()
        self.db.refresh(cart)
        return cart

    def get_or_create(self, user_id: int) -> Cart:
        cart = self.get_by_user_id(user_id)
        if not cart:
            cart = self.create_for_user(user_id)
        return cart

    def delete(self, user_id: int) -> bool:
        cart = self.get_by_user_id(user_id)
        if cart:
            self.db.delete(cart)
            self.db.commit()
            return True
        return False
