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
    CONFIRMED = "confirmed"


class RoomStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
