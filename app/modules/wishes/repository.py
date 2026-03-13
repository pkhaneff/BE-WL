import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.db.models.wish import Wish, WishHistory
from app.shared.enums import WishType, WishStatus


class WishRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, wish: Wish) -> Wish:
        self._db.add(wish)
        self._db.flush()
        return wish

    def get_by_id(self, wish_id: uuid.UUID) -> Wish | None:
        stmt = select(Wish).where(
            and_(Wish.id == wish_id, Wish.deleted_at.is_(None))
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_room(
        self,
        room_id: uuid.UUID,
        wish_type: WishType | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Wish], int]:
        from sqlalchemy import func, or_

        base_filter = and_(
            Wish.room_id == room_id,
            Wish.deleted_at.is_(None),
        )
        conditions = [base_filter]
        if wish_type:
            conditions.append(Wish.wish_type == wish_type)
        if search:
            conditions.append(Wish.title.ilike(f"%{search}%"))

        combined = and_(*conditions)
        count_stmt = select(func.count()).select_from(Wish).where(combined)
        total = self._db.execute(count_stmt).scalar_one()

        stmt = (
            select(Wish)
            .where(combined)
            .offset(offset)
            .limit(limit)
            .order_by(Wish.created_at.desc())
        )
        items = list(self._db.execute(stmt).scalars().all())
        return items, total

    def update(self, wish: Wish) -> Wish:
        self._db.flush()
        return wish

    def soft_delete(self, wish: Wish) -> None:
        wish.deleted_at = datetime.now(timezone.utc)
        self._db.flush()


class WishHistoryRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, entry: WishHistory) -> WishHistory:
        self._db.add(entry)
        self._db.flush()
        return entry

    def get_by_room(
        self, room_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> tuple[list[WishHistory], int]:
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(WishHistory).where(
            WishHistory.room_id == room_id
        )
        total = self._db.execute(count_stmt).scalar_one()
        stmt = (
            select(WishHistory)
            .where(WishHistory.room_id == room_id)
            .offset(offset)
            .limit(limit)
            .order_by(WishHistory.confirmed_at.desc())
        )
        items = list(self._db.execute(stmt).scalars().all())
        return items, total
