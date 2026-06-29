from typing import Optional

from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.repositories.base import Repository


class UserProfileRepository(Repository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = UserProfile

    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def get_by_id(self, profile_id: int) -> Optional[UserProfile]:
        return self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()

    def create(self, **kwargs) -> UserProfile:
        return super().create(UserProfile, **kwargs)

    def update(self, profile_id: int, **kwargs) -> Optional[UserProfile]:
        return super().update(UserProfile, profile_id, **kwargs)

    def delete(self, profile_id: int) -> bool:
        return super().delete(UserProfile, profile_id)
