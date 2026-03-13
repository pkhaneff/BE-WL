from app.core.exceptions import DomainError, ApplicationError


class AuthError(ApplicationError):
    """Lỗi xác thực chung."""
    pass


class InvalidCredentialsError(AuthError):
    def __init__(self) -> None:
        super().__init__(code="INVALID_CREDENTIALS", message="Email hoặc mật khẩu không đúng.")


class EmailAlreadyExistsError(AuthError):
    def __init__(self, email: str) -> None:
        super().__init__(
            code="EMAIL_EXISTS",
            message=f"Email '{email}' đã được sử dụng.",
        )


class UsernameAlreadyExistsError(AuthError):
    def __init__(self, username: str) -> None:
        super().__init__(
            code="USERNAME_EXISTS",
            message=f"Username '{username}' đã được sử dụng.",
        )


class TokenBlacklistedError(AuthError):
    def __init__(self) -> None:
        super().__init__(code="TOKEN_BLACKLISTED", message="Token đã bị vô hiệu hóa.")
