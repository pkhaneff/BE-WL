import uuid

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DBSession
from app.modules.rooms.schemas import (
    RoomCreate,
    RoomJoinRequest,
    RoomResponse,
    RoomMemberResponse,
    RoomSettingsUpdate,
    RoomSettingsResponse,
)
from app.modules.rooms.service import RoomService
from app.modules.rooms.repository import RoomRepository
from app.modules.users.repository import UserRepository

router = APIRouter(prefix="/rooms", tags=["Rooms"])


def _build_room_response(room, db) -> RoomResponse:
    repo = RoomRepository(db)
    user_repo = UserRepository(db)
    active_members = repo.get_active_members(room.id)

    member_responses = []
    for m in active_members:
        user = user_repo.get_by_id(m.user_id)
        if user:
            member_responses.append(
                RoomMemberResponse(
                    user_id=m.user_id,
                    username=user.username,
                    full_name=user.full_name,
                    avatar_url=user.avatar_url,
                    joined_at=m.joined_at,
                )
            )

    return RoomResponse(
        id=room.id,
        name=room.name,
        join_code=room.join_code,
        created_by=room.created_by,
        is_active=room.is_active,
        created_at=room.created_at,
        updated_at=room.updated_at,
        active_members=member_responses,
    )


@router.post("", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_room(payload: RoomCreate, current_user: CurrentUser, db: DBSession) -> RoomResponse:
    service = RoomService(db)
    room = service.create_room(payload, current_user.id)
    return _build_room_response(room, db)


@router.get("/me", response_model=RoomResponse | None)
def get_my_room(current_user: CurrentUser, db: DBSession) -> RoomResponse | None:
    service = RoomService(db)
    room = service.get_current_room(current_user.id)
    if not room:
        return None
    return _build_room_response(room, db)


@router.get("/{room_id}", response_model=RoomResponse)
def get_room(room_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> RoomResponse:
    service = RoomService(db)
    room = service.get_room(room_id)
    return _build_room_response(room, db)


@router.post("/join", response_model=RoomResponse)
def join_room(payload: RoomJoinRequest, current_user: CurrentUser, db: DBSession) -> RoomResponse:
    service = RoomService(db)
    room = service.join_room(payload, current_user.id)
    return _build_room_response(room, db)


@router.post("/{room_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_room(room_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> None:
    service = RoomService(db)
    service.leave_room(room_id, current_user.id)


@router.get("/{room_id}/settings", response_model=RoomSettingsResponse)
def get_room_settings(
    room_id: uuid.UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> RoomSettingsResponse:
    service = RoomService(db)
    room, total_wishes, total_completed_wishes = service.get_room_settings(room_id, current_user.id)
    return RoomSettingsResponse(
        room_id=room.id,
        name=room.name,
        join_code=room.join_code,
        is_active=room.is_active,
        total_wishes=total_wishes,
        total_completed_wishes=total_completed_wishes,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


@router.patch("/{room_id}/settings", response_model=RoomSettingsResponse)
def update_room_settings(
    room_id: uuid.UUID,
    payload: RoomSettingsUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> RoomSettingsResponse:
    service = RoomService(db)
    room, total_wishes, total_completed_wishes = service.update_room_settings(
        room_id, current_user.id, payload
    )
    return RoomSettingsResponse(
        room_id=room.id,
        name=room.name,
        join_code=room.join_code,
        is_active=room.is_active,
        total_wishes=total_wishes,
        total_completed_wishes=total_completed_wishes,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


@router.post("/{room_id}/settings/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_room_from_settings(room_id: uuid.UUID, current_user: CurrentUser, db: DBSession) -> None:
    service = RoomService(db)
    service.leave_room(room_id, current_user.id)
