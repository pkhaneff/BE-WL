import uuid

from sqlalchemy.orm import Session

from app.db.models.notification import Notification
from app.modules.notifications.exceptions import NotRoomMemberError
from app.modules.notifications.repository import NotificationRepository
from app.modules.rooms.repository import RoomRepository
from app.shared.enums import NotificationEventType


class NotificationService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = NotificationRepository(db)
        self._room_repo = RoomRepository(db)

    def _assert_room_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> None:
        membership = self._room_repo.get_membership(room_id, user_id)
        if not membership:
            raise NotRoomMemberError()

    def _resolve_partner_id(self, room_id: uuid.UUID, actor_id: uuid.UUID) -> uuid.UUID | None:
        active_members = self._room_repo.get_active_members(room_id)
        for member in active_members:
            if member.user_id != actor_id:
                return member.user_id
        return None

    def create_room_partner_notification(
        self,
        room_id: uuid.UUID,
        actor_id: uuid.UUID,
        event_type: NotificationEventType,
        title: str,
        message: str,
        wish_id: uuid.UUID | None = None,
    ) -> Notification | None:
        recipient_id = self._resolve_partner_id(room_id, actor_id)
        if not recipient_id:
            return None

        notification = Notification(
            room_id=room_id,
            wish_id=wish_id,
            actor_id=actor_id,
            recipient_id=recipient_id,
            event_type=event_type,
            title=title,
            message=message,
            is_read=False,
        )
        return self._repo.create(notification)

    def get_room_notifications(
        self,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int]:
        self._assert_room_member(room_id, user_id)
        offset = (page - 1) * page_size
        return self._repo.get_by_recipient_and_room(
            recipient_id=user_id,
            room_id=room_id,
            offset=offset,
            limit=page_size,
        )

    def mark_all_room_notifications_as_read(
        self,
        room_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> int:
        self._assert_room_member(room_id, user_id)
        updated_count = self._repo.mark_all_as_read(recipient_id=user_id, room_id=room_id)
        self._db.commit()
        return updated_count
