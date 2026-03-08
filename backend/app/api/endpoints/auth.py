
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import get_session
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserRead

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_access_token(
    session: AsyncSession = Depends(get_session), 
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 兼容的 token 登录，支持用邮箱或用户名登录。"""
    # 先按邮箱查找
    statement = select(User).where(User.email == form_data.username)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    # 如果按邮箱没找到，再按用户名查
    if user is None:
        statement = select(User).where(User.username == form_data.username)
        result = await session.execute(statement)
        user = result.scalar_one_or_none()
    
    # 验证密码
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查状态
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserRead)
async def register_user(
    *,
    session: AsyncSession = Depends(get_session),
    user_in: UserCreate,
) -> Any:
    """
    注册新用户
    """
    # 检查邮箱是否已存在
    statement = select(User).where((User.email == user_in.email) | (User.username == user_in.username))
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system",
        )

    # 安全限制：禁止通过公开注册接口创建管理员账号
    if user_in.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot register admin via public endpoint",
        )
    
    # 创建用户：先生成密码哈希，再构造 User 实例
    hashed_password = security.get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        role=user_in.role,
        hashed_password=hashed_password,
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
