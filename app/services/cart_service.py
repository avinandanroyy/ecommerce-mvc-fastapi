from typing import Optional, List, Tuple
from sqlalchemy.orm import Session

from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.repositories.product_repository import ProductRepository
from app.models.cart_item import CartItems


class CartService:
    def __init__(self, db: Session):
        self.cart_repo = CartRepository(db)
        self.cart_item_repo = CartItemRepository(db)
        self.product_repo = ProductRepository(db)

    def get_cart(self, user_id: int) -> dict:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            return {"id": None, "user_id": user_id, "items": [], "total_amount": 0.0}

        items = self.cart_item_repo.get_by_cart(cart.id)
        item_list = []
        total_amount = 0.0

        for item in items:
            product = self.product_repo.get_by_id(item.product_id)
            if product:
                item_list.append({
                    "id": item.id,
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "product_name": product.name,
                    "product_price": product.price,
                    "product_image": product.image_url,
                    "created_at": item.created_at,
                })
                total_amount += item.quantity * product.price

        return {
            "id": cart.id,
            "user_id": cart.user_id,
            "items": item_list,
            "total_amount": round(total_amount, 2),
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
        }

    def add_item(self, user_id: int, product_id: int, quantity: int = 1) -> dict:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            cart = self.cart_repo.create_for_user(user_id)

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if quantity > product.stock_quantity:
            raise ValueError("Insufficient stock quantity")

        existing_item = self.cart_item_repo.get_by_cart_and_product(cart.id, product_id)

        if existing_item:
            existing_item.quantity += quantity
            if existing_item.quantity > product.stock_quantity:
                raise ValueError("Exceeds available stock")
            self.cart_item_repo.db.commit()
            self.cart_item_repo.db.refresh(existing_item)
        else:
            existing_item = self.cart_item_repo.create(cart.id, product_id, quantity)

        return self.get_cart(user_id)

    def remove_item(self, user_id: int, product_id: int) -> dict:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            raise ValueError("Cart not found")

        self.cart_item_repo.delete_by_cart_and_product(cart.id, product_id)
        return self.get_cart(user_id)

    def update_item(self, user_id: int, product_id: int, quantity: int) -> dict:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            raise ValueError("Cart not found")

        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        if quantity > product.stock_quantity:
            raise ValueError("Exceeds available stock")

        cart_item = self.cart_item_repo.get_by_cart_and_product(cart.id, product_id)
        if not cart_item:
            raise ValueError("Item not found in cart")

        cart_item.quantity = quantity
        self.cart_item_repo.db.commit()
        self.cart_item_repo.db.refresh(cart_item)

        return self.get_cart(user_id)

    def clear_cart(self, user_id: int) -> bool:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            return True

        self.cart_item_repo.db.query(CartItems).filter(CartItems.cart_id == cart.id).delete()
        self.cart_item_repo.db.commit()
        return True

    def get_cart_item_count(self, user_id: int) -> int:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            return 0
        return self.cart_item_repo.get_cart_items_count(cart.id)

    def calculate_total(self, user_id: int) -> float:
        cart = self.cart_repo.get_by_user_id(user_id)
        if not cart:
            return 0.0
        return self.cart_item_repo.get_total(cart.id)
