
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.models.user import UserRole

# 共享属性
class UserBase(BaseModel):
    username: str
    email: str
    role: UserRole = UserRole.STUDENT
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

# 创建用户时接收的数据
class UserCreate(UserBase):
    password: str

# 返回给前端的用户数据 (不包含密码)
class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_approved: bool


class UserUpdate(BaseModel):
    """管理员更新用户信息时使用的字段（全部可选）。"""
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_approved: Optional[bool] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserUpdateMe(BaseModel):
    """用户自己更新个人信息。"""
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    # Password change usually done separately


class UserChangePassword(BaseModel):
    old_password: str
    new_password: str


# JWT Token 格式
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
