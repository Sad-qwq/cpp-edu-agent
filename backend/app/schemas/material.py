from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class MaterialCreate(BaseModel):
    title: str
    description: Optional[str] = None
    class_id: int


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str] = None
    file_url: str
    file_type: str
    size: Optional[int] = None
    class_id: int
    uploader_id: int
    created_at: datetime


class MaterialListResponse(BaseModel):
    items: List[MaterialRead]
    total: int
