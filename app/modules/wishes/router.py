import uuid

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, DBSession
from app.modules.wishes.schemas import (
    WishCreate,
    WishFilterParams,
    WishHistoryResponse,
    WishResponse,
    WishUpdate,
)
from app.modules.wishes.service import WishService
from app.shared.enums import WishType
from app.shared.pagination import PagedResponse

router = APIRouter(prefix="/rooms/{room_id}/wishes", tags=["Wishes"])


@router.get("", response_model=PagedResponse[WishResponse])
def get_wishes(
    room_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    wish_type: WishType | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[WishResponse]:
    service = WishService(db)
    params = WishFilterParams(wish_type=wish_type, search=search, page=page, page_size=page_size)
    items, total = service.get_wishes(room_id, current_user.id, params)
    return PagedResponse.create(
        items=[WishResponse.model_validate(w) for w in items],
        total=total,
        params=params,
    )


@router.post("", response_model=WishResponse, status_code=status.HTTP_201_CREATED)
def create_wish(
    room_id: uuid.UUID,
    payload: WishCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> WishResponse:
    service = WishService(db)
    wish = service.create_wish(room_id, payload, current_user.id)
    return WishResponse.model_validate(wish)


@router.get("/history", response_model=PagedResponse[WishHistoryResponse])
def get_wish_history(
    room_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[WishHistoryResponse]:
    service = WishService(db)
    items, total = service.get_wish_history(room_id, current_user.id, page, page_size)
    from app.shared.pagination import PageParams
    return PagedResponse.create(
        items=[WishHistoryResponse.model_validate(h) for h in items],
        total=total,
        params=PageParams(page=page, page_size=page_size),
    )


@router.get("/{wish_id}", response_model=WishResponse)
def get_wish(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> WishResponse:
    service = WishService(db)
    wish = service.get_wish(room_id, wish_id, current_user.id)
    return WishResponse.model_validate(wish)


@router.put("/{wish_id}", response_model=WishResponse)
def update_wish(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    payload: WishUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> WishResponse:
    service = WishService(db)
    wish = service.update_wish(room_id, wish_id, payload, current_user.id)
    return WishResponse.model_validate(wish)


@router.delete("/{wish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wish(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> None:
    service = WishService(db)
    service.delete_wish(room_id, wish_id, current_user.id)


@router.post("/{wish_id}/confirm", response_model=WishHistoryResponse)
def confirm_wish(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> WishHistoryResponse:
    service = WishService(db)
    history = service.confirm_wish(room_id, wish_id, current_user.id)
    return WishHistoryResponse.model_validate(history)
