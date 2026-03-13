import uuid

from fastapi import APIRouter, Query

from app.api.deps import AdminUser, DBSession
from app.modules.admin.schemas import (
    AdminRoomDetail,
    AdminStatsResponse,
    AdminUserDetail,
    AdminWishResponse,
)
from app.modules.admin.selectors import AdminSelector
from app.shared.pagination import PagedResponse, PageParams

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_stats(admin: AdminUser, db: DBSession) -> AdminStatsResponse:
    selector = AdminSelector(db)
    return AdminStatsResponse(**selector.get_stats())


@router.get("/users", response_model=PagedResponse[AdminUserDetail])
def list_users(
    admin: AdminUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[AdminUserDetail]:
    selector = AdminSelector(db)
    params = PageParams(page=page, page_size=page_size)
    users, total = selector.get_all_users(offset=params.offset, limit=params.page_size)
    return PagedResponse.create(
        items=[AdminUserDetail.model_validate(u) for u in users],
        total=total,
        params=params,
    )


@router.get("/users/{user_id}", response_model=AdminUserDetail)
def get_user_detail(user_id: uuid.UUID, admin: AdminUser, db: DBSession) -> AdminUserDetail:
    from app.core.exceptions import NotFoundError
    selector = AdminSelector(db)
    user, history = selector.get_user_with_room_history(user_id)
    if not user:
        raise NotFoundError("User", str(user_id))
    result = AdminUserDetail.model_validate(user)
    result.room_history = history
    return result


@router.get("/rooms", response_model=PagedResponse[AdminRoomDetail])
def list_rooms(
    admin: AdminUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[AdminRoomDetail]:
    selector = AdminSelector(db)
    params = PageParams(page=page, page_size=page_size)
    rooms, total = selector.get_all_rooms(offset=params.offset, limit=params.page_size)

    items = []
    for r in rooms:
        count = selector.get_room_active_member_count(r.id)
        items.append(AdminRoomDetail(
            id=r.id,
            name=r.name,
            created_by=r.created_by,
            is_active=r.is_active,
            created_at=r.created_at,
            active_member_count=count,
        ))
    return PagedResponse.create(items=items, total=total, params=params)


@router.get("/rooms/{room_id}/wishes", response_model=PagedResponse[AdminWishResponse])
def get_room_wishes(
    room_id: uuid.UUID,
    admin: AdminUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[AdminWishResponse]:
    selector = AdminSelector(db)
    params = PageParams(page=page, page_size=page_size)
    wishes, total = selector.get_room_wishes(
        room_id, offset=params.offset, limit=params.page_size
    )
    return PagedResponse.create(
        items=[AdminWishResponse.model_validate(w) for w in wishes],
        total=total,
        params=params,
    )
