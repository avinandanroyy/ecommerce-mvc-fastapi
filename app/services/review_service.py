from typing import Optional, List
from sqlalchemy.orm import Session

from app.repositories.review_repository import ReviewRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.models.review import Review


class ReviewService:
    def __init__(self, db: Session):
        self.review_repo = ReviewRepository(db)
        self.product_repo = ProductRepository(db)
        self.user_repo = UserRepository(db)

    def create_review(self, user_id: int, product_id: int, rating: float, review_text: Optional[str] = None) -> Review:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        existing_review = self.review_repo.get_by_user_and_product(user_id, product_id)
        if existing_review:
            raise ValueError("You have already reviewed this product")

        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        return self.review_repo.create(user_id, product_id, rating, review_text)

    def get_review(self, review_id: int) -> Optional[Review]:
        review = self.review_repo.get_by_id(review_id)
        if not review:
            raise ValueError("Review not found")
        return review

    def update_review(self, review_id: int, user_id: int, rating: Optional[float] = None, review_text: Optional[str] = None) -> Optional[Review]:
        review = self.get_review(review_id)
        if review.user_id != user_id:
            raise ValueError("You can only update your own reviews")

        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")

        return self.review_repo.update_review(review_id, rating, review_text)

    def delete_review(self, review_id: int, user_id: int) -> bool:
        review = self.get_review(review_id)
        if review.user_id != user_id:
            raise ValueError("You can only delete your own reviews")

        return self.review_repo.delete(review_id)

    def get_reviews_by_product(self, product_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        return self.review_repo.get_by_product(product_id, skip, limit)

    def get_reviews_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return self.review_repo.get_by_user(user_id, skip, limit)

    def get_product_stats(self, product_id: int) -> dict:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        average_rating = self.review_repo.get_average_rating(product_id)
        total_reviews = self.review_repo.get_review_count(product_id)

        return {
            "product_id": product_id,
            "average_rating": round(average_rating, 2) if average_rating else None,
            "total_reviews": total_reviews,
        }

    def search_reviews_by_product(self, product_id: int, query: str, skip: int = 0, limit: int = 100) -> List[Review]:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        return (
            self.review_repo.db.query(Review)
            .filter(Review.product_id == product_id, Review.review_text.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
