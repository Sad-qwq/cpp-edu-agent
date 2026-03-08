from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.api import deps
from app.db.session import get_session
from app.models.announcement import Announcement
from app.models.user import User, UserRole
from app.schemas.announcement import AnnouncementCreate, AnnouncementRead, AnnouncementUpdate

router = APIRouter()


@router.get("/public", response_model=List[AnnouncementRead])
async def list_public_announcements(
    *,
    session: AsyncSession = Depends(get_session),
    limit: int = 10,
) -> Any:
    limit = max(1, min(limit, 50))
    stmt = (
        select(Announcement)
        .where(Announcement.class_id.is_(None), Announcement.is_active == True)  # noqa: E712
        .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/", response_model=List[AnnouncementRead])
async def list_announcements_admin(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
    include_inactive: bool = False,
    keyword: Optional[str] = None,
) -> Any:
    stmt = select(Announcement).where(Announcement.class_id.is_(None))
    if not include_inactive:
        stmt = stmt.where(Announcement.is_active == True)  # noqa: E712
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where((Announcement.title.ilike(like)) | (Announcement.content.ilike(like)))
    stmt = stmt.order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=AnnouncementRead)
async def create_announcement_admin(
    announcement_in: AnnouncementCreate,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    announcement = Announcement(
        class_id=None,
        title=announcement_in.title,
        content=announcement_in.content,
        is_pinned=announcement_in.is_pinned,
        is_active=announcement_in.is_active,
        created_by=current_user.id,
    )
    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement


@router.patch("/{announcement_id}", response_model=AnnouncementRead)
async def update_announcement_admin(
    announcement_id: int,
    announcement_in: AnnouncementUpdate,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    announcement = await session.get(Announcement, announcement_id)
    if not announcement or announcement.class_id is not None:
        raise HTTPException(status_code=404, detail="Announcement not found")

    update_data = announcement_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement_admin(
    announcement_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> None:
    announcement = await session.get(Announcement, announcement_id)
    if not announcement or announcement.class_id is not None:
        raise HTTPException(status_code=404, detail="Announcement not found")

    announcement.is_active = False
    session.add(announcement)
    await session.commit()
