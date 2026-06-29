from typing import Optional, List

from sqlalchemy.orm import Session

from app.repositories.user_profile_repository import UserProfileRepository
from app.models.user_profile import UserProfile
from app.models.user import User


class UserProfileService:
    def __init__(self, db: Session):
        self.repo = UserProfileRepository(db)

    def get_by_user_id(self, user_id: int) -> Optional[UserProfile]:
        return self.repo.get_by_user_id(user_id)

    def create_or_update(self, user_id: int, phone: Optional[str] = None, address: Optional[str] = None, city: Optional[str] = None, country: Optional[str] = None, zip_code: Optional[str] = None) -> Optional[UserProfile]:
        existing_profile = self.repo.get_by_user_id(user_id)
        if existing_profile:
            return self.repo.update(existing_profile.id, phone=phone, address=address, city=city, country=country, zip_code=zip_code)

        user = self.repo.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        profile = UserProfile(user_id=user_id, phone=phone, address=address, city=city, country=country, zip_code=zip_code)
        self.repo.db.add(profile)
        self.repo.db.commit()
        self.repo.db.refresh(profile)
        return profile

    def delete(self, user_id: int) -> bool:
        profile = self.get_by_user_id(user_id)
        if not profile:
            raise ValueError("Profile not found")
        return self.repo.delete(profile.id)
