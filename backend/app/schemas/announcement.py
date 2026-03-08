from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnnouncementBase(BaseModel):
    class_id: Optional[int] = None
    title: str
    content: str
    is_pinned: bool = False
    is_active: bool = True


class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_active: Optional[bool] = None


class AnnouncementRead(AnnouncementBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    created_by: int
