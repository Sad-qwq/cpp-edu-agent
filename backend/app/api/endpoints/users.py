
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.db.session import get_session
from app.models.user import User
from app.schemas.user import UserRead

router = APIRouter()

@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user

@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_admin), # 仅管理员可查看所有用户
    session: AsyncSession = Depends(get_session),
) -> Any:
    """
    获取所有用户列表 (管理员权限)
    """
    statement = select(User).offset(skip).limit(limit)
    result = await session.execute(statement)
    users = result.scalars().all()
    return users
