import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db.session import engine
from app.models.user import User, UserRole
from app.core.security import get_password_hash


ADMIN_EMAIL = "sadbo12005@outlook.com"
ADMIN_NAME = "admin"
ADMIN_PASSWORD = "123456"


async def create_admin() -> None:
    async_session = AsyncSession(bind=engine, expire_on_commit=False)

    async with async_session as session:
        # 1. 检查是否已存在该邮箱的用户
        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        existing = result.scalar_one_or_none()
        if existing:
            if existing.role != UserRole.ADMIN or existing.username != ADMIN_NAME:
                print(
                    f"[WARN] 用户存在但角色/用户名不符合管理员要求 (role={existing.role}, username={existing.username})，将校正为管理员账号"
                )
                existing.role = UserRole.ADMIN
                existing.username = ADMIN_NAME
                existing.is_approved = True
                existing.is_active = True
                session.add(existing)
                await session.commit()
                print(f"[OK] 已校正 {existing.email} 为管理员 (username={ADMIN_NAME})")
            else:
                print(f"[INFO] 用户已存在且为管理员: {existing.email}")
            return

        # 2. 创建新的管理员用户
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin_user = User(
            username=ADMIN_NAME,
            email=ADMIN_EMAIL,
            role=UserRole.ADMIN,
            is_active=True,
            is_approved=True,
            hashed_password=hashed_password,
        )

        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        print("[OK] 已创建管理员账号:")
        print(f"  email: {admin_user.email}")
        print(f"  username : {admin_user.username}")
        print(f"  role : {admin_user.role}")


if __name__ == "__main__":
    asyncio.run(create_admin())
