
from pydantic import BaseModel
from typing import Optional
from app.models.user import UserRole

# 共享属性
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT

# 创建用户时接收的数据
class UserCreate(UserBase):
    password: str

# 返回给前端的用户数据 (不包含密码)
class UserRead(UserBase):
    id: int
    is_active: bool
    is_approved: bool

# JWT Token 格式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
