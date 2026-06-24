import secrets
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.logging import get_logger
from app.core.security import hash_password, verify_password
from app.db.models.room import Room
from app.modules.rooms.exceptions import (
    JoinCodeGenerationError,
    RoomFullError,
    RoomNotActiveError,
    RoomPasswordInvalidError,
    UserAlreadyInRoomError,
    UserNotInRoomError,
)
from app.modules.rooms.repository import RoomRepository
from app.modules.rooms.schemas import RoomCreate, RoomJoinRequest, RoomSettingsUpdate

logger = get_logger(__name__)

MAX_ROOM_MEMBERS = 2
JOIN_CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
JOIN_CODE_LENGTH = 7
MAX_JOIN_CODE_ATTEMPTS = 10


class RoomService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = RoomRepository(db)

    def _generate_join_code(self) -> str:
        return "".join(secrets.choice(JOIN_CODE_CHARS) for _ in range(JOIN_CODE_LENGTH))

    def create_room(self, payload: RoomCreate, creator_id: uuid.UUID) -> Room:
        # Creator phải chưa active ở room nào
        existing = self._repo.get_active_membership(creator_id)
        if existing:
            raise UserAlreadyInRoomError()

        attempts = 0
        room: Room | None = None
        while attempts < MAX_JOIN_CODE_ATTEMPTS:
            join_code = self._generate_join_code()
            room = Room(
                name=payload.name,
                created_by=creator_id,
                join_code=join_code,
                room_password_hash=hash_password(payload.pass_room),
            )
            try:
                self._repo.create(room)
                break
            except IntegrityError:
                self._db.rollback()
                attempts += 1
                room = None

        if room is None:
            raise JoinCodeGenerationError()

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

    def join_room(self, payload: RoomJoinRequest, user_id: uuid.UUID) -> Room:
        room = self._repo.get_by_join_code(payload.join_code)
        if not room:
            raise NotFoundError("Room", payload.join_code)
        if not room.is_active:
            raise RoomNotActiveError()
        if not verify_password(payload.pass_room, room.room_password_hash):
            raise RoomPasswordInvalidError()

        # Kiểm tra user đang active ở room nào chưa
        active_membership = self._repo.get_active_membership(user_id)
        if active_membership:
            raise UserAlreadyInRoomError()

        # Kiểm tra room đã đủ người chưa
        active_count = self._repo.count_active_members(room.id)
        if active_count >= MAX_ROOM_MEMBERS:
            raise RoomFullError()

        self._repo.add_member(room.id, user_id)
        self._db.commit()
        self._db.refresh(room)

        logger.info("room_joined", room_id=str(room.id), user_id=str(user_id))
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

    def get_room_settings(self, room_id: uuid.UUID, user_id: uuid.UUID) -> tuple[Room, int, int]:
        room = self._repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room", str(room_id))

        membership = self._repo.get_membership(room_id, user_id)
        if not membership:
            raise UserNotInRoomError()

        total_wishes, total_completed_wishes = self._repo.get_wish_stats(room_id)
        return room, total_wishes, total_completed_wishes

    def update_room_settings(
        self, room_id: uuid.UUID, user_id: uuid.UUID, payload: RoomSettingsUpdate
    ) -> tuple[Room, int, int]:
        room = self._repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room", str(room_id))

        membership = self._repo.get_membership(room_id, user_id)
        if not membership:
            raise UserNotInRoomError()

        if room.created_by != user_id:
            raise PermissionDeniedError("Chỉ chủ phòng mới có thể cập nhật cài đặt phòng.")

        if payload.name is not None:
            room.name = payload.name
        if payload.pass_room is not None:
            room.room_password_hash = hash_password(payload.pass_room)
        if payload.is_active is not None:
            room.is_active = payload.is_active

        self._db.commit()
        self._db.refresh(room)

        total_wishes, total_completed_wishes = self._repo.get_wish_stats(room_id)
        logger.info("room_settings_updated", room_id=str(room_id), user_id=str(user_id))
        return room, total_wishes, total_completed_wishes
