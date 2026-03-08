from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class AnnouncementBase(SQLModel):
    class_id: Optional[int] = Field(default=None, foreign_key="classroom.id", nullable=True)
    title: str
    content: str
    is_pinned: bool = False
    is_active: bool = True


class Announcement(AnnouncementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: int = Field(foreign_key="user.id")
