import uuid
from sqlalchemy.orm import Session

import redis as redis_client

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.exceptions import InvalidTokenError
from app.core.logging import get_logger
from app.db.models.user import User
from app.modules.auth.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    UsernameAlreadyExistsError,
    TokenBlacklistedError,
)
from app.modules.auth.schemas import RegisterRequest, TokenResponse, AccessTokenResponse
from app.modules.users.repository import UserRepository

logger = get_logger(__name__)

_REFRESH_TOKEN_PREFIX = "refresh_token:"


def _get_redis() -> redis_client.Redis:
    return redis_client.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
    )


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._user_repo = UserRepository(db)
        self._redis = _get_redis()

    def register(self, payload: RegisterRequest) -> TokenResponse:
        if self._user_repo.get_by_email(payload.email):
            raise EmailAlreadyExistsError(payload.email)
        if self._user_repo.get_by_username(payload.username):
            raise UsernameAlreadyExistsError(payload.username)

        user = User(
            email=payload.email,
            username=payload.username,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
        self._user_repo.create(user)
        self._db.commit()
        self._db.refresh(user)

        logger.info("user_registered", user_id=str(user.id), email=user.email)
        return self._issue_tokens(user)

    def login(self, email: str, password: str) -> TokenResponse:
        user = self._user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()

        logger.info("user_login", user_id=str(user.id))
        return self._issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except InvalidTokenError:
            return  # Token đã hết hạn, không cần làm gì

        jti = payload.get("jti") or refresh_token[-32:]
        key = f"{_REFRESH_TOKEN_PREFIX}{jti}"
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
        self._redis.setex(key, ttl, "blacklisted")
        logger.info("user_logout", jti=jti)

    def refresh_token(self, refresh_token_str: str) -> AccessTokenResponse:
        try:
            payload = decode_token(refresh_token_str)
        except InvalidTokenError as exc:
            raise exc

        if payload.get("type") != "refresh":
            from app.core.exceptions import InvalidTokenError as ITE
            raise ITE("Token không đúng loại.")

        jti = payload.get("jti") or refresh_token_str[-32:]
        key = f"{_REFRESH_TOKEN_PREFIX}{jti}"
        if self._redis.exists(key):
            raise TokenBlacklistedError()

        user_id = payload.get("sub")
        user = self._user_repo.get_by_id(uuid.UUID(user_id))
        if user is None or not user.is_active:
            from app.core.exceptions import InvalidTokenError as ITE
            raise ITE("Người dùng không hợp lệ.")

        access_token = create_access_token({"sub": str(user.id)})
        return AccessTokenResponse(access_token=access_token)

    def _issue_tokens(self, user: User) -> TokenResponse:
        import secrets
        jti = secrets.token_hex(16)
        token_payload = {"sub": str(user.id), "jti": jti}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
