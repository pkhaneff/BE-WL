import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.users.schemas import UserListItem


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    pass_room: str = Field(min_length=1, max_length=128)


class RoomJoinRequest(BaseModel):
    join_code: str = Field(
        min_length=7,
        max_length=7,
        pattern=r"^[ABCDEFGHJKLMNPQRSTUVWXYZ23456789]{7}$",
    )
    pass_room: str = Field(min_length=1, max_length=128)


class RoomSettingsUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    pass_room: str | None = Field(default=None, min_length=1, max_length=128)
    is_active: bool | None = None


class RoomSettingsResponse(BaseModel):
    room_id: uuid.UUID
    name: str
    join_code: str
    is_active: bool
    total_wishes: int
    total_completed_wishes: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RoomMemberResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    full_name: str | None
    avatar_url: str | None = None
    joined_at: datetime

    model_config = {"from_attributes": True}


class RoomResponse(BaseModel):
    id: uuid.UUID
    name: str
    join_code: str
    created_by: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    active_members: list[RoomMemberResponse] = []

    model_config = {"from_attributes": True}


class RoomListItem(BaseModel):
    id: uuid.UUID
    name: str
    created_by: uuid.UUID
    is_active: bool
    created_at: datetime
    member_count: int = 0

    model_config = {"from_attributes": True}
