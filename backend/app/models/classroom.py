from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ClassroomBase(SQLModel):
    name: str
    invite_code: str = Field(index=True, unique=True)
    is_active: bool = True


class Classroom(ClassroomBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ClassMembershipBase(SQLModel):
    is_active: bool = True


class ClassMembership(ClassMembershipBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="classroom.id")
    student_id: int = Field(foreign_key="user.id")
    joined_at: datetime = Field(default_factory=datetime.utcnow)
