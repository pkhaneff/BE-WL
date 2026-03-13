import uuid
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.models.user import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserProfileUpdate


class UserProfileService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = UserRepository(db)

    def get_profile(self, user_id: uuid.UUID) -> User:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    def update_profile(self, user_id: uuid.UUID, payload: UserProfileUpdate) -> User:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url

        self._repo.update(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def deactivate_account(self, user_id: uuid.UUID) -> None:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        user.is_active = False
        self._repo.update(user)
        self._db.commit()
