from app.core.exceptions import DomainError


class NotRoomMemberError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code="NOT_ROOM_MEMBER",
            message="Bạn không phải thành viên active của phòng này.",
        )
