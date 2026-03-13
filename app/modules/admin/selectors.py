import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.db.models.user import User
from app.db.models.room import Room, RoomMember
from app.db.models.wish import Wish, WishHistory
from app.shared.enums import WishStatus


class AdminSelector:
    """
    Read-only query service cho admin.
    Chứa các query phức tạp của admin dashboard/report.
    Không chứa business logic.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def get_all_users(self, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        total = self._db.execute(select(func.count()).select_from(User)).scalar_one()
        stmt = select(User).offset(offset).limit(limit).order_by(User.created_at.desc())
        items = list(self._db.execute(stmt).scalars().all())
        return items, total

    def get_user_with_room_history(self, user_id: uuid.UUID) -> tuple[User | None, list[dict]]:
        user = self._db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        if not user:
            return None, []

        memberships = list(
            self._db.execute(
                select(RoomMember, Room)
                .join(Room, RoomMember.room_id == Room.id)
                .where(RoomMember.user_id == user_id)
                .order_by(RoomMember.joined_at.desc())
            ).all()
        )

        history = [
            {
                "room_id": str(m.RoomMember.room_id),
                "room_name": m.Room.name,
                "joined_at": m.RoomMember.joined_at.isoformat(),
                "left_at": m.RoomMember.left_at.isoformat() if m.RoomMember.left_at else None,
            }
            for m in memberships
        ]
        return user, history

    def get_all_rooms(self, offset: int = 0, limit: int = 20) -> tuple[list[Room], int]:
        total = self._db.execute(select(func.count()).select_from(Room)).scalar_one()
        stmt = select(Room).offset(offset).limit(limit).order_by(Room.created_at.desc())
        items = list(self._db.execute(stmt).scalars().all())
        return items, total

    def get_room_active_member_count(self, room_id: uuid.UUID) -> int:
        return self._db.execute(
            select(func.count()).select_from(RoomMember).where(
                and_(RoomMember.room_id == room_id, RoomMember.left_at.is_(None))
            )
        ).scalar_one()

    def get_room_wishes(
        self, room_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[Wish], int]:
        total = self._db.execute(
            select(func.count()).select_from(Wish).where(
                and_(Wish.room_id == room_id, Wish.deleted_at.is_(None))
            )
        ).scalar_one()
        stmt = (
            select(Wish)
            .where(and_(Wish.room_id == room_id, Wish.deleted_at.is_(None)))
            .offset(offset)
            .limit(limit)
            .order_by(Wish.created_at.desc())
        )
        items = list(self._db.execute(stmt).scalars().all())
        return items, total

    def get_stats(self) -> dict:
        total_users = self._db.execute(select(func.count()).select_from(User)).scalar_one()
        total_rooms = self._db.execute(select(func.count()).select_from(Room)).scalar_one()
        total_active_rooms = self._db.execute(
            select(func.count()).select_from(Room).where(Room.is_active.is_(True))
        ).scalar_one()
        total_wishes = self._db.execute(
            select(func.count()).select_from(Wish).where(Wish.deleted_at.is_(None))
        ).scalar_one()
        total_confirmed = self._db.execute(
            select(func.count()).select_from(Wish).where(
                and_(Wish.status == WishStatus.CONFIRMED, Wish.deleted_at.is_(None))
            )
        ).scalar_one()
        return {
            "total_users": total_users,
            "total_rooms": total_rooms,
            "total_active_rooms": total_active_rooms,
            "total_wishes": total_wishes,
            "total_confirmed_wishes": total_confirmed,
        }
