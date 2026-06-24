import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.db.models.room import Room, RoomMember
from app.db.models.wish import Wish
from app.shared.enums import WishStatus


class RoomRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, room: Room) -> Room:
        self._db.add(room)
        self._db.flush()
        return room

    def get_by_id(self, room_id: uuid.UUID) -> Room | None:
        stmt = select(Room).where(Room.id == room_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_join_code(self, join_code: str) -> Room | None:
        stmt = select(Room).where(Room.join_code == join_code)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_all(self, offset: int = 0, limit: int = 20) -> tuple[list[Room], int]:
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(Room)
        total = self._db.execute(count_stmt).scalar_one()
        stmt = select(Room).offset(offset).limit(limit).order_by(Room.created_at.desc())
        items = list(self._db.execute(stmt).scalars().all())
        return items, total

    def get_active_members(self, room_id: uuid.UUID) -> list[RoomMember]:
        stmt = select(RoomMember).where(
            and_(RoomMember.room_id == room_id, RoomMember.left_at.is_(None))
        )
        return list(self._db.execute(stmt).scalars().all())

    def count_active_members(self, room_id: uuid.UUID) -> int:
        from sqlalchemy import func
        stmt = select(func.count()).select_from(RoomMember).where(
            and_(RoomMember.room_id == room_id, RoomMember.left_at.is_(None))
        )
        return self._db.execute(stmt).scalar_one()

    def get_active_membership(self, user_id: uuid.UUID) -> RoomMember | None:
        """Kiểm tra user có đang active trong room nào không."""
        stmt = select(RoomMember).where(
            and_(RoomMember.user_id == user_id, RoomMember.left_at.is_(None))
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def get_membership(self, room_id: uuid.UUID, user_id: uuid.UUID) -> RoomMember | None:
        stmt = select(RoomMember).where(
            and_(
                RoomMember.room_id == room_id,
                RoomMember.user_id == user_id,
                RoomMember.left_at.is_(None),
            )
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def add_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> RoomMember:
        member = RoomMember(
            room_id=room_id,
            user_id=user_id,
            joined_at=datetime.now(timezone.utc),
        )
        self._db.add(member)
        self._db.flush()
        return member

    def leave_room(self, member: RoomMember) -> None:
        member.left_at = datetime.now(timezone.utc)
        self._db.flush()

    def get_user_room_history(self, user_id: uuid.UUID) -> list[RoomMember]:
        stmt = (
            select(RoomMember)
            .where(RoomMember.user_id == user_id)
            .order_by(RoomMember.joined_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def get_wish_stats(self, room_id: uuid.UUID) -> tuple[int, int]:
        from sqlalchemy import func, case

        stmt = select(
            func.count(Wish.id),
            func.coalesce(
                func.sum(case((Wish.status == WishStatus.CONFIRMED, 1), else_=0)),
                0,
            ),
        ).where(
            and_(
                Wish.room_id == room_id,
                Wish.status != WishStatus.DELETED,
                Wish.deleted_at.is_(None),
            )
        )
        total_wishes, total_completed_wishes = self._db.execute(stmt).one()
        return int(total_wishes), int(total_completed_wishes)
