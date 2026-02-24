
from enum import Enum
from typing import Optional
from sqlmodel import Field, SQLModel

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    role: UserRole = Field(default=UserRole.STUDENT)
    is_active: bool = True
    is_approved: bool = False # 教师需要审核

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
