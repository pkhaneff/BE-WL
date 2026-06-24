import uuid
from datetime import datetime, timezone

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, notification: Notification) -> Notification:
        self._db.add(notification)
        self._db.flush()
        return notification

    def get_by_recipient_and_room(
        self,
        recipient_id: uuid.UUID,
        room_id: uuid.UUID,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Notification], int]:
        from sqlalchemy import func

        combined = and_(
            Notification.recipient_id == recipient_id,
            Notification.room_id == room_id,
        )

        count_stmt = select(func.count()).select_from(Notification).where(combined)
        total = self._db.execute(count_stmt).scalar_one()

        stmt = (
            select(Notification)
            .where(combined)
            .offset(offset)
            .limit(limit)
            .order_by(Notification.created_at.desc())
        )
        items = list(self._db.execute(stmt).scalars().all())
        return items, total

    def mark_all_as_read(self, recipient_id: uuid.UUID, room_id: uuid.UUID) -> int:
        stmt = select(Notification).where(
            and_(
                Notification.recipient_id == recipient_id,
                Notification.room_id == room_id,
                Notification.is_read.is_(False),
            )
        )
        items = list(self._db.execute(stmt).scalars().all())
        if not items:
            return 0

        read_at = datetime.now(timezone.utc)
        for item in items:
            item.is_read = True
            item.read_at = read_at

        self._db.flush()
        return len(items)
