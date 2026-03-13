import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.shared.enums import UserRole, WishType, WishStatus


class AdminUserDetail(BaseModel):
    id: uuid.UUID
    email: EmailStr
    username: str
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    room_history: list[dict] = []

    model_config = {"from_attributes": True}


class AdminRoomDetail(BaseModel):
    id: uuid.UUID
    name: str
    created_by: uuid.UUID
    is_active: bool
    created_at: datetime
    active_member_count: int = 0

    model_config = {"from_attributes": True}


class AdminStatsResponse(BaseModel):
    total_users: int
    total_rooms: int
    total_active_rooms: int
    total_wishes: int
    total_confirmed_wishes: int


class AdminWishResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    created_by: uuid.UUID
    title: str
    wish_type: WishType
    status: WishStatus
    created_at: datetime

    model_config = {"from_attributes": True}
