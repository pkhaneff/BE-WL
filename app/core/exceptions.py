"""
Phân cấp exception theo nguyên tắc của rule.md:
- DomainError: vi phạm business rule ở domain/service layer
- ApplicationError: lỗi ở application/use-case layer
- InfrastructureError: lỗi kết nối DB, cache, external service
- InvalidTokenError: token không hợp lệ (dùng ở security layer)
"""


class AppBaseError(Exception):
    """Base exception cho toàn bộ ứng dụng."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class DomainError(AppBaseError):
    """Vi phạm business rule ở domain layer."""

    pass


class ApplicationError(AppBaseError):
    """Lỗi ở application/service layer."""

    pass


class InfrastructureError(AppBaseError):
    """Lỗi infrastructure: DB, cache, external service."""

    pass


class InvalidTokenError(AppBaseError):
    """Token JWT không hợp lệ hoặc hết hạn."""

    def __init__(self, message: str = "Token không hợp lệ") -> None:
        super().__init__(code="INVALID_TOKEN", message=message)


class NotFoundError(DomainError):
    """Resource không tìm thấy."""

    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} không tìm thấy: {identifier}",
        )


class PermissionDeniedError(DomainError):
    """Không có quyền thực hiện hành động này."""

    def __init__(self, message: str = "Không có quyền thực hiện hành động này") -> None:
        super().__init__(code="PERMISSION_DENIED", message=message)


class ConflictError(DomainError):
    """Xung đột dữ liệu."""

    def __init__(self, message: str) -> None:
        super().__init__(code="CONFLICT", message=message)


class ValidationError(ApplicationError):
    """Lỗi validate nghiệp vụ."""

    def __init__(self, message: str) -> None:
        super().__init__(code="VALIDATION_ERROR", message=message)
