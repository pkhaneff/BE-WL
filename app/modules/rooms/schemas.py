import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.users.schemas import UserListItem


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class RoomMemberResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    full_name: str | None
    joined_at: datetime

    model_config = {"from_attributes": True}


class RoomResponse(BaseModel):
    id: uuid.UUID
    name: str
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
