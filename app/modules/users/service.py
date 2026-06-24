import uuid
from typing import BinaryIO

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import InfrastructureError, NotFoundError, ValidationError
from app.db.models.user import User
from app.infrastructure.storage.s3_uploader import S3Uploader
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserProfileUpdate

_ALLOWED_AVATAR_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


class UserProfileService:
    def __init__(self, db: Session, s3_uploader: S3Uploader | None = None) -> None:
        self._db = db
        self._repo = UserRepository(db)
        self._s3_uploader = s3_uploader

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

    def update_avatar(
        self,
        user_id: uuid.UUID,
        *,
        fileobj: BinaryIO,
        filename: str,
        content_type: str | None,
    ) -> User:
        if not self._s3_uploader:
            raise InfrastructureError(
                code="S3_NOT_CONFIGURED",
                message="Chưa cấu hình S3 uploader.",
            )

        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))

        if content_type and content_type not in _ALLOWED_AVATAR_CONTENT_TYPES:
            raise ValidationError(
                "Avatar không đúng định dạng ảnh (jpeg/png/webp/gif)."
            )

        uploaded = self._s3_uploader.upload_fileobj(
            fileobj,
            filename=filename,
            key_prefix=settings.S3_PREFIX_AVATAR_USER,
            content_type=content_type,
            extra_path=str(user_id),
        )

        user.avatar_url = uploaded.url
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
