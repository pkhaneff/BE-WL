from app.core.exceptions import DomainError


class RoomFullError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="ROOM_FULL",
            message="Phòng đã đủ 2 thành viên.",
        )


class UserAlreadyInRoomError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="USER_ALREADY_IN_ROOM",
            message="Bạn đang active trong một phòng khác. Hãy rời phòng đó trước.",
        )


class UserNotInRoomError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="USER_NOT_IN_ROOM",
            message="Bạn không phải thành viên active của phòng này.",
        )


class RoomNotActiveError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="ROOM_NOT_ACTIVE",
            message="Phòng không còn hoạt động.",
        )


class RoomPasswordInvalidError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="ROOM_PASSWORD_INVALID",
            message="Mật khẩu phòng không đúng.",
        )


class JoinCodeGenerationError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="JOIN_CODE_GENERATION_FAILED",
            message="Không thể tạo join code cho phòng. Vui lòng thử lại.",
        )
