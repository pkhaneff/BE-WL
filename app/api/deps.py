import uuid
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import InvalidTokenError, PermissionDeniedError
from app.core.security import decode_token
from app.db.session import get_db
from app.infrastructure.storage.s3_uploader import S3Uploader
from app.modules.users.repository import UserRepository
from app.shared.enums import UserRole
from app.db.models.user import User
from sqlalchemy.orm import Session

http_bearer = HTTPBearer(auto_error=False)

DBSession = Annotated[Session, Depends(get_db)]


@lru_cache
def get_s3_uploader() -> S3Uploader:
    return S3Uploader.from_settings()


S3UploaderDep = Annotated[S3Uploader, Depends(get_s3_uploader)]


def _get_current_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(http_bearer)],
    db: DBSession,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa xác thực. Vui lòng đăng nhập.",
        )
    try:
        payload = decode_token(credentials.credentials)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
        ) from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không đúng loại.",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ.",
        )

    repo = UserRepository(db)
    user = repo.get_by_id(uuid.UUID(user_id_str))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Người dùng không tồn tại hoặc đã bị vô hiệu hóa.",
        )
    return user


CurrentUser = Annotated[User, Depends(_get_current_user_from_token)]


def get_admin_user(current_user: CurrentUser) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ admin mới có quyền truy cập.",
        )
    return current_user


AdminUser = Annotated[User, Depends(get_admin_user)]
