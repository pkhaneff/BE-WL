import uuid
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.models.room import Room
from app.modules.rooms.exceptions import (
    RoomFullError,
    RoomNotActiveError,
    UserAlreadyInRoomError,
    UserNotInRoomError,
)
from app.modules.rooms.repository import RoomRepository
from app.modules.rooms.schemas import RoomCreate

logger = get_logger(__name__)

MAX_ROOM_MEMBERS = 2


class RoomService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = RoomRepository(db)

    def create_room(self, payload: RoomCreate, creator_id: uuid.UUID) -> Room:
        # Creator phải chưa active ở room nào
        existing = self._repo.get_active_membership(creator_id)
        if existing:
            raise UserAlreadyInRoomError()

        room = Room(name=payload.name, created_by=creator_id)
        self._repo.create(room)
        # Creator tự động tham gia vào room
        self._repo.add_member(room.id, creator_id)
        self._db.commit()
        self._db.refresh(room)

        logger.info("room_created", room_id=str(room.id), creator_id=str(creator_id))
        return room

    def get_room(self, room_id: uuid.UUID) -> Room:
        room = self._repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room", str(room_id))
        return room

    def get_current_room(self, user_id: uuid.UUID) -> Room | None:
        membership = self._repo.get_active_membership(user_id)
        if not membership:
            return None
        return self._repo.get_by_id(membership.room_id)

    def join_room(self, room_id: uuid.UUID, user_id: uuid.UUID) -> Room:
        room = self._repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room", str(room_id))
        if not room.is_active:
            raise RoomNotActiveError()

        # Kiểm tra user đang active ở room nào chưa
        active_membership = self._repo.get_active_membership(user_id)
        if active_membership:
            raise UserAlreadyInRoomError()

        # Kiểm tra room đã đủ người chưa
        active_count = self._repo.count_active_members(room_id)
        if active_count >= MAX_ROOM_MEMBERS:
            raise RoomFullError()

        self._repo.add_member(room_id, user_id)
        self._db.commit()
        self._db.refresh(room)

        logger.info("room_joined", room_id=str(room_id), user_id=str(user_id))
        return room

    def leave_room(self, room_id: uuid.UUID, user_id: uuid.UUID) -> None:
        room = self._repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room", str(room_id))

        member = self._repo.get_membership(room_id, user_id)
        if not member:
            raise UserNotInRoomError()

        self._repo.leave_room(member)

        # Nếu không còn ai trong room, đánh inactive
        active_count = self._repo.count_active_members(room_id)
        if active_count == 0:
            room.is_active = False

        self._db.commit()
        logger.info("room_left", room_id=str(room_id), user_id=str(user_id))
