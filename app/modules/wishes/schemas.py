import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.enums import WishType, WishStatus


class WishCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = Field(default=None)
    wish_type: WishType


class WishUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    wish_type: WishType | None = None


class WishResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    created_by: uuid.UUID
    creator_name: str | None = None
    title: str
    description: str | None
    wish_type: WishType
    status: WishStatus
    confirmed_by: uuid.UUID | None
    confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WishHistoryResponse(BaseModel):
    id: uuid.UUID
    wish_id: uuid.UUID
    room_id: uuid.UUID
    created_by: uuid.UUID
    confirmed_by: uuid.UUID
    title: str
    description: str | None
    wish_type: WishType
    action: WishStatus
    confirmed_at: datetime

    model_config = {"from_attributes": True}


class WishFilterParams(BaseModel):
    wish_type: WishType | None = None
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
