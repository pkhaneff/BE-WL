import uuid

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, DBSession
from app.modules.wishes.schemas import (
    WishCreate,
    WishFilterParams,
    WishHistoryResponse,
    WishResponse,
    WishUpdate,
)
from app.modules.wishes.service import WishService
from app.modules.users.repository import UserRepository
from app.shared.enums import WishStatus, WishType
from app.shared.pagination import PagedResponse, PageParams

router = APIRouter(prefix="/rooms/{room_id}/wishes", tags=["Wishes"])


def _resolve_display_name(full_name: str | None, username: str) -> str:
    if full_name and full_name.strip():
        return full_name
    return username


def _build_wish_response(wish, user_repo: UserRepository) -> WishResponse:
    creator = user_repo.get_by_id(wish.created_by)
    creator_name = None
    if creator:
        creator_name = _resolve_display_name(creator.full_name, creator.username)
    return WishResponse.model_validate(wish).model_copy(update={"creator_name": creator_name})


def _build_wish_responses(wishes: list, user_repo: UserRepository) -> list[WishResponse]:
    creator_ids = list({wish.created_by for wish in wishes})
    creators = user_repo.get_by_ids(creator_ids)
    creator_name_map = {
        user.id: _resolve_display_name(user.full_name, user.username) for user in creators
    }
    responses: list[WishResponse] = []
    for wish in wishes:
        responses.append(
            WishResponse.model_validate(wish).model_copy(
                update={"creator_name": creator_name_map.get(wish.created_by)}
            )
        )
    return responses


@router.get("", response_model=PagedResponse[WishResponse])
def get_wishes(
    room_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    status: str | None = Query(default=None),
    wish_type: WishType | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[WishResponse]:
    service = WishService(db)
    user_repo = UserRepository(db)
    statuses = None
    if status:
        status_values = [value.strip() for value in status.split(",") if value.strip()]
        statuses = []
        for value in status_values:
            try:
                statuses.append(WishStatus(value))
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=f"Invalid status: {value}") from exc
    params = WishFilterParams(wish_type=wish_type, search=search, page=page, page_size=page_size)
    items, total = service.get_wishes(room_id, current_user.id, params, statuses=statuses)
    return PagedResponse.create(
        items=_build_wish_responses(items, user_repo),
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
    user_repo = UserRepository(db)
    wish = service.create_wish(room_id, payload, current_user.id)
    return _build_wish_response(wish, user_repo)


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
    user_repo = UserRepository(db)
    wish = service.get_wish(room_id, wish_id, current_user.id)
    return _build_wish_response(wish, user_repo)


@router.put("/{wish_id}", response_model=WishResponse)
def update_wish(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    payload: WishUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> WishResponse:
    service = WishService(db)
    user_repo = UserRepository(db)
    wish = service.update_wish(room_id, wish_id, payload, current_user.id)
    return _build_wish_response(wish, user_repo)


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


@router.post("/{wish_id}/request-confirmation", response_model=WishResponse)
def request_wish_confirmation(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> WishResponse:
    service = WishService(db)
    user_repo = UserRepository(db)
    wish = service.request_confirm(room_id, wish_id, current_user.id)
    return _build_wish_response(wish, user_repo)


@router.post("/{wish_id}/reject", response_model=WishResponse)
def reject_wish_confirmation(
    room_id: uuid.UUID,
    wish_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> WishResponse:
    service = WishService(db)
    user_repo = UserRepository(db)
    wish = service.reject_confirm(room_id, wish_id, current_user.id)
    return _build_wish_response(wish, user_repo)
