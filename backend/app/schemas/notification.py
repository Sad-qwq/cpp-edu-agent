from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationBase(BaseModel):
    title: str
    content: str
    link: str | None = None


class NotificationRead(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_read: bool
    created_at: datetime


class NotificationUpdate(BaseModel):
    is_read: bool | None = None
