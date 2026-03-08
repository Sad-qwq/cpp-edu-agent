from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class ClassroomBase(BaseModel):
    name: str


class ClassroomCreate(ClassroomBase):
    pass


class ClassroomRead(ClassroomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invite_code: str
    teacher_id: int
    teacher_name: str | None = None
    is_active: bool
    created_at: datetime
    student_count: int | None = None
    assignment_count: int | None = None
    already_joined: bool | None = None


class JoinClassRequest(BaseModel):
    invite_code: str
