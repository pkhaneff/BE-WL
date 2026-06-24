import uuid

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DBSession
from app.modules.notifications.schemas import NotificationReadAllResponse, NotificationResponse
from app.modules.notifications.service import NotificationService
from app.shared.pagination import PageParams, PagedResponse

router = APIRouter(prefix="/rooms/{room_id}/notifications", tags=["Notifications"])


@router.get("", response_model=PagedResponse[NotificationResponse])
def get_room_notifications(
    room_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PagedResponse[NotificationResponse]:
    service = NotificationService(db)
    items, total = service.get_room_notifications(room_id, current_user.id, page, page_size)

    return PagedResponse.create(
        items=[NotificationResponse.model_validate(item) for item in items],
        total=total,
        params=PageParams(page=page, page_size=page_size),
    )


@router.post("/read-all", response_model=NotificationReadAllResponse)
def mark_all_notifications_as_read(
    room_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> NotificationReadAllResponse:
    service = NotificationService(db)
    updated_count = service.mark_all_room_notifications_as_read(room_id, current_user.id)
    return NotificationReadAllResponse(updated_count=updated_count)
