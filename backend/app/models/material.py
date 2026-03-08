from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class MaterialBase(SQLModel):
    title: str
    description: Optional[str] = None
    file_url: str
    file_type: str
    size: Optional[int] = None
    class_id: int = Field(foreign_key="classroom.id")
    uploader_id: int = Field(foreign_key="user.id")


class Material(MaterialBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
