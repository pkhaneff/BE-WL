# Import all models here so Alembic can detect them
from app.db.models.user import User  # noqa: F401
from app.db.models.room import Room, RoomMember  # noqa: F401
from app.db.models.wish import Wish, WishHistory  # noqa: F401
from app.db.models.notification import Notification  # noqa: F401

__all__ = ["User", "Room", "RoomMember", "Wish", "WishHistory", "Notification"]
