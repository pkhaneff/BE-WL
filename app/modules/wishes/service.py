import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.core.logging import get_logger
from app.db.models.wish import Wish, WishHistory
from app.modules.rooms.repository import RoomRepository
from app.modules.wishes.exceptions import (
    CannotConfirmOwnWishError,
    CannotModifyOthersWishError,
    NotRoomMemberError,
    WishAlreadyConfirmedError,
    WishNotFoundError,
)
from app.modules.wishes.repository import WishHistoryRepository, WishRepository
from app.modules.wishes.schemas import WishCreate, WishFilterParams, WishUpdate
from app.shared.enums import WishStatus

logger = get_logger(__name__)


class WishService:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._repo = WishRepository(db)
        self._history_repo = WishHistoryRepository(db)
        self._room_repo = RoomRepository(db)

    def _assert_room_member(self, room_id: uuid.UUID, user_id: uuid.UUID) -> None:
        membership = self._room_repo.get_membership(room_id, user_id)
        if not membership:
            raise NotRoomMemberError()

    def create_wish(
        self, room_id: uuid.UUID, payload: WishCreate, creator_id: uuid.UUID
    ) -> Wish:
        self._assert_room_member(room_id, creator_id)

        wish = Wish(
            room_id=room_id,
            created_by=creator_id,
            title=payload.title,
            description=payload.description,
            wish_type=payload.wish_type,
            status=WishStatus.PENDING,
        )
        self._repo.create(wish)
        self._db.commit()
        self._db.refresh(wish)

        logger.info("wish_created", wish_id=str(wish.id), room_id=str(room_id))
        return wish

    def get_wishes(
        self, room_id: uuid.UUID, user_id: uuid.UUID, params: WishFilterParams
    ) -> tuple[list[Wish], int]:
        self._assert_room_member(room_id, user_id)
        offset = (params.page - 1) * params.page_size
        return self._repo.get_by_room(
            room_id=room_id,
            wish_type=params.wish_type,
            search=params.search,
            offset=offset,
            limit=params.page_size,
        )

    def get_wish(self, room_id: uuid.UUID, wish_id: uuid.UUID, user_id: uuid.UUID) -> Wish:
        self._assert_room_member(room_id, user_id)
        wish = self._repo.get_by_id(wish_id)
        if not wish or wish.room_id != room_id:
            raise WishNotFoundError(str(wish_id))
        return wish

    def update_wish(
        self, room_id: uuid.UUID, wish_id: uuid.UUID, payload: WishUpdate, user_id: uuid.UUID
    ) -> Wish:
        self._assert_room_member(room_id, user_id)
        wish = self._repo.get_by_id(wish_id)
        if not wish or wish.room_id != room_id:
            raise WishNotFoundError(str(wish_id))
        if wish.created_by != user_id:
            raise CannotModifyOthersWishError()

        if payload.title is not None:
            wish.title = payload.title
        if payload.description is not None:
            wish.description = payload.description
        if payload.wish_type is not None:
            wish.wish_type = payload.wish_type

        self._repo.update(wish)
        self._db.commit()
        self._db.refresh(wish)
        return wish

    def delete_wish(
        self, room_id: uuid.UUID, wish_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        self._assert_room_member(room_id, user_id)
        wish = self._repo.get_by_id(wish_id)
        if not wish or wish.room_id != room_id:
            raise WishNotFoundError(str(wish_id))
        if wish.created_by != user_id:
            raise CannotModifyOthersWishError()
        self._repo.soft_delete(wish)
        self._db.commit()

    def confirm_wish(
        self, room_id: uuid.UUID, wish_id: uuid.UUID, confirmed_by: uuid.UUID
    ) -> WishHistory:
        """
        Chỉ đối phương (không phải người tạo wish) mới được confirm.
        Khi confirm → tạo WishHistory snapshot + cập nhật Wish.status = CONFIRMED.
        """
        self._assert_room_member(room_id, confirmed_by)
        wish = self._repo.get_by_id(wish_id)
        if not wish or wish.room_id != room_id:
            raise WishNotFoundError(str(wish_id))
        if wish.created_by == confirmed_by:
            raise CannotConfirmOwnWishError()
        if wish.status == WishStatus.CONFIRMED:
            raise WishAlreadyConfirmedError()

        now = datetime.now(timezone.utc)
        wish.status = WishStatus.CONFIRMED
        wish.confirmed_by = confirmed_by
        wish.confirmed_at = now
        self._repo.update(wish)

        history = WishHistory(
            wish_id=wish.id,
            room_id=wish.room_id,
            created_by=wish.created_by,
            confirmed_by=confirmed_by,
            title=wish.title,
            description=wish.description,
            wish_type=wish.wish_type,
            confirmed_at=now,
        )
        self._history_repo.create(history)
        self._db.commit()
        self._db.refresh(history)

        logger.info("wish_confirmed", wish_id=str(wish_id), confirmed_by=str(confirmed_by))
        return history

    def get_wish_history(
        self, room_id: uuid.UUID, user_id: uuid.UUID, page: int = 1, page_size: int = 20
    ) -> tuple[list[WishHistory], int]:
        self._assert_room_member(room_id, user_id)
        offset = (page - 1) * page_size
        return self._history_repo.get_by_room(room_id, offset=offset, limit=page_size)
