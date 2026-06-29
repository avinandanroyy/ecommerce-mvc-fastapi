from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.review import Review
from app.repositories.base import Repository


class ReviewRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Review

    def get_by_id(self, review_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.id == review_id).first()

    def get_by_user_and_product(self, user_id: int, product_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.user_id == user_id, Review.product_id == product_id).first()

    def get_by_product(self, product_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return self.db.query(Review).filter(Review.product_id == product_id).offset(skip).limit(limit).all()

    def get_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        return self.db.query(Review).filter(Review.user_id == user_id).offset(skip).limit(limit).all()

    def create(self, user_id: int, product_id: int, rating: float, review_text: Optional[str] = None) -> Review:
        review = Review(user_id=user_id, product_id=product_id, rating=rating, review_text=review_text)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def update(self, review_id: int, **kwargs) -> Optional[Review]:
        return super().update(Review, review_id, **kwargs)

    def delete(self, review_id: int) -> bool:
        return super().delete(Review, review_id)

    def get_average_rating(self, product_id: int) -> Optional[float]:
        from sqlalchemy import func
        result = self.db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
        return result if result else None

    def get_review_count(self, product_id: int) -> int:
        return self.db.query(Review).filter(Review.product_id == product_id).count()

    def update_review(self, review_id: int, rating: Optional[float] = None, review_text: Optional[str] = None) -> Optional[Review]:
        review = self.get_by_id(review_id)
        if review:
            if rating is not None:
                review.rating = rating
            if review_text is not None:
                review.review_text = review_text
            self.db.commit()
            self.db.refresh(review)
        return review
