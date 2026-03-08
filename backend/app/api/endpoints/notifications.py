from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.db.session import get_session
from app.models.notification import Notification
from app.schemas.notification import NotificationRead, NotificationUpdate
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[NotificationRead])
async def list_my_notifications(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/{notification_id}/read", response_model=NotificationRead)
async def mark_notification_read(
    notification_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    notification = await session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification.is_read = True
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


@router.post("/read_all")
async def mark_all_read(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    stmt = select(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)  # noqa: E712
    result = await session.execute(stmt)
    notifications = result.scalars().all()
    for n in notifications:
        n.is_read = True
        session.add(n)
    await session.commit()
    return {"updated": len(notifications)}
