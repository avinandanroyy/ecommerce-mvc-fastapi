from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.models.user import User
from app.repositories.base import Repository


class UserRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = User

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, **kwargs) -> User:
        return super().create(User, **kwargs)

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        return super().update(User, user_id, **kwargs)

    def delete(self, user_id: int) -> bool:
        return super().delete(User, user_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        return super().get_all(User, skip, limit)

    def get_active_users(self) -> List[User]:
        return self.db.query(User).filter(User.is_active == 1).all()

    def search_by_email_or_name(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            self.db.query(User)
            .filter(or_(User.email.ilike(f"%{query}%"), User.name.ilike(f"%{query}%")))
            .offset(skip)
            .limit(limit)
            .all()
        )
