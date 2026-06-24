import uuid
from datetime import datetime

from pydantic import BaseModel

from app.shared.enums import NotificationEventType


class NotificationResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    wish_id: uuid.UUID | None
    actor_id: uuid.UUID
    recipient_id: uuid.UUID
    event_type: NotificationEventType
    title: str
    message: str
    is_read: bool
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationReadAllResponse(BaseModel):
    updated_count: int
