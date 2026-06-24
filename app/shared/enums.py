import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class WishType(str, enum.Enum):
    GIFT = "gift"                  # Quà muốn được đối phương tặng
    HABIT = "habit"                # Thói quen muốn đối phương nên có
    BAD_HABIT = "bad_habit"        # Tật xấu muốn đối phương nên bỏ
    QUESTION = "question"          # Câu hỏi muốn đối phương trả lời


class WishStatus(str, enum.Enum):
    PENDING = "pending"
    REQUESTED = "requested"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"
    DELETED = "deleted"


class RoomStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class NotificationEventType(str, enum.Enum):
    WISH_CREATED = "wish_created"
    WISH_UPDATED = "wish_updated"
    WISH_CONFIRM_REQUESTED = "wish_confirm_requested"
    WISH_CONFIRMED = "wish_confirmed"
