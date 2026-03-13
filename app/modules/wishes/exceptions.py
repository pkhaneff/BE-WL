from app.core.exceptions import DomainError


class WishNotFoundError(DomainError):
    def __init__(self, wish_id: str) -> None:
        super().__init__(code="WISH_NOT_FOUND", message=f"Wish không tìm thấy: {wish_id}")


class WishAlreadyConfirmedError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="WISH_ALREADY_CONFIRMED",
            message="Wish này đã được xác nhận rồi.",
        )


class CannotConfirmOwnWishError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="CANNOT_CONFIRM_OWN_WISH",
            message="Bạn không thể tự xác nhận wish của chính mình. Đối phương mới có thể confirm.",
        )


class NotRoomMemberError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="NOT_ROOM_MEMBER",
            message="Bạn không phải thành viên active của phòng này.",
        )


class CannotModifyOthersWishError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="CANNOT_MODIFY_OTHERS_WISH",
            message="Bạn không thể sửa/xóa wish của người khác.",
        )
