from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password, get_password_hash
from app.repositories.user_repository import UserRepository
from app.repositories.user_profile_repository import UserProfileRepository


class UserService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.user_profile_repo = UserProfileRepository(db)

    def register(self, email: str, password: str, name: str) -> Optional[User]:
        existing_user = self.user_repo.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        user = self.user_repo.create(
            email=email,
            password_hash=get_password_hash(password),
            name=name,
            role="customer",
        )
        return user

    def login(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        return user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_by_id(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_by_email(email)

    def update_profile(self, user_id: int, **kwargs) -> Optional[User]:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return self.user_repo.update(user_id, **kwargs)

    def update_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not verify_password(old_password, user.password_hash):
            raise ValueError("Invalid old password")
        user.password_hash = get_password_hash(new_password)
        self.user_repo.db.commit()
        self.user_repo.db.refresh(user)
        return True

    def delete_user(self, user_id: int) -> bool:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return self.user_repo.delete(user_id)

    def list_all(self, skip: int = 0, limit: int = 100) -> list:
        return self.user_repo.list_all(skip, limit)
