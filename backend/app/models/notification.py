from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class NotificationBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    title: str
    content: str
    link: str | None = None


class Notification(NotificationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime
