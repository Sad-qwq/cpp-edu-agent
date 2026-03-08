from typing import Any, List
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.api import deps
from app.db.session import get_session
from app.models.classroom import Classroom, ClassMembership
from app.models.assignment import Assignment
from app.models.user import User, UserRole
from app.models.announcement import Announcement
from app.models.notification import Notification
from app.schemas.classroom import ClassroomCreate, ClassroomRead, JoinClassRequest
from app.schemas.user import UserRead
from app.schemas.announcement import AnnouncementCreate, AnnouncementRead, AnnouncementUpdate

router = APIRouter()


def _generate_invite_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.get("/join/preview", response_model=ClassroomRead)
async def preview_classroom_by_invite_code(
    invite_code: str,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """根据邀请码预览班级信息，避免填错码；需登录。"""
    result = await session.execute(
        select(Classroom).where(
            Classroom.invite_code == invite_code,
            Classroom.is_active == True,  # noqa: E712
        )
    )
    classroom = result.scalar_one_or_none()
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found or inactive")

    # 教师名称
    teacher = await session.get(User, classroom.teacher_id)
    teacher_name = teacher.username if teacher else "Unknown"

    # 是否已加入（学生场景下给友好提示）
    already_joined = False
    if current_user.role == UserRole.STUDENT:
        membership_stmt = select(ClassMembership).where(
            ClassMembership.class_id == classroom.id,
            ClassMembership.student_id == current_user.id,
            ClassMembership.is_active == True,  # noqa: E712
        )
        membership = (await session.execute(membership_stmt)).scalar_one_or_none()
        already_joined = membership is not None

    payload = classroom.dict()
    payload["teacher_name"] = teacher_name
    payload["student_count"] = None
    payload["assignment_count"] = None
    payload["already_joined"] = already_joined
    return payload


@router.post("/", response_model=ClassroomRead)
async def create_classroom(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    classroom_in: ClassroomCreate,
) -> Any:
    """教师或管理员创建班级，自动生成邀请码。"""
    if current_user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teacher or admin can create classroom",
        )

    # 生成唯一的邀请码
    for _ in range(5):
        code = _generate_invite_code()
        result = await session.execute(select(Classroom).where(Classroom.invite_code == code))
        if result.scalar_one_or_none() is None:
            invite_code = code
            break
    else:
        raise HTTPException(status_code=500, detail="Failed to generate invite code")

    classroom = Classroom(
        name=classroom_in.name,
        invite_code=invite_code,
        teacher_id=current_user.id,
    )
    session.add(classroom)
    await session.commit()
    await session.refresh(classroom)
    return classroom


@router.get("/teaching", response_model=List[ClassroomRead])
async def list_my_classrooms(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师/管理员查看自己创建的班级。"""
    if current_user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Only teacher or admin can view teaching classrooms")

    result = await session.execute(
        select(Classroom).where(
            Classroom.teacher_id == current_user.id,
            Classroom.is_active == True,  # noqa: E712
        )
    )
    classrooms = result.scalars().all()
    return classrooms


@router.post("/join", response_model=ClassroomRead)
async def join_classroom(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    join_in: JoinClassRequest,
) -> Any:
    """学生通过邀请码加入班级。"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only student can join classroom")

    result = await session.execute(
        select(Classroom).where(
            Classroom.invite_code == join_in.invite_code,
            Classroom.is_active == True,  # noqa: E712
        )
    )
    classroom = result.scalar_one_or_none()
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found or inactive")

    # 检查是否已在班级中
    result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == classroom.id,
            ClassMembership.student_id == current_user.id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership:
        if not membership.is_active:
            membership.is_active = True
            session.add(membership)
            await session.commit()
            await session.refresh(membership)
        return classroom

    membership = ClassMembership(class_id=classroom.id, student_id=current_user.id)
    session.add(membership)
    await session.commit()
    return classroom


@router.get("/my", response_model=List[ClassroomRead])
async def list_my_joined_classrooms(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """学生查看自己加入的班级列表。"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only student can view joined classrooms")

    result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.student_id == current_user.id,
            ClassMembership.is_active == True,  # noqa: E712
        )
    )
    memberships = result.scalars().all()
    if not memberships:
        return []

    class_ids = [m.class_id for m in memberships]
    result = await session.execute(
        select(Classroom).where(
            Classroom.id.in_(class_ids),
            Classroom.is_active == True,  # noqa: E712
        )
    )
    classrooms = result.scalars().all()
    return classrooms


@router.get("/{class_id}", response_model=ClassroomRead)
async def get_classroom(
    class_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取单个班级详情（需为该班成员或教师/管理员）。"""
    result = await session.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalar_one_or_none()
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # 权限检查
    has_permission = False
    if current_user.role == UserRole.ADMIN:
        has_permission = True
    elif classroom.teacher_id == current_user.id:
        has_permission = True
    else:
        # 检查是否为成员
        result = await session.execute(
            select(ClassMembership).where(
                ClassMembership.class_id == class_id,
                ClassMembership.student_id == current_user.id,
                ClassMembership.is_active == True, # noqa: E712
            )
        )
        membership = result.scalar_one_or_none()
        if membership:
            has_permission = True
            
    if not has_permission:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 获取教师名称
    teacher = await session.get(User, classroom.teacher_id)
    teacher_name = teacher.username if teacher else "Unknown"

    response = classroom.dict()
    response["teacher_name"] = teacher_name

    # 统计学生人数与作业数量，便于前端概览展示
    student_count_stmt = select(func.count(ClassMembership.id)).where(
        ClassMembership.class_id == class_id,
        ClassMembership.is_active == True,  # noqa: E712
    )
    assignment_count_stmt = select(func.count(Assignment.id)).where(Assignment.classroom_id == class_id)

    student_count = (await session.execute(student_count_stmt)).scalar_one()
    assignment_count = (await session.execute(assignment_count_stmt)).scalar_one()

    response["student_count"] = student_count
    response["assignment_count"] = assignment_count
    return response


@router.get("/{class_id}/students", response_model=List[UserRead])
async def list_classroom_students(
    class_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师/管理员查看班级学生名单。"""
    # 检查班级是否存在
    result = await session.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalar_one_or_none()
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # 权限：必须是该班级教师或管理员
    if current_user.role != UserRole.ADMIN and classroom.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 查询成员关系
    result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == class_id,
            ClassMembership.is_active == True,  # noqa: E712
        )
    )
    memberships = result.scalars().all()
    if not memberships:
        return []

    student_ids = [m.student_id for m in memberships]
    result = await session.execute(select(User).where(User.id.in_(student_ids)))
    students = result.scalars().all()
    return students


@router.delete("/{class_id}/students/{student_id}")
async def remove_student_from_classroom(
    class_id: int,
    student_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师/管理员将学生移出班级（软删除）。"""
    # 检查班级是否存在
    result = await session.execute(select(Classroom).where(Classroom.id == class_id))
    classroom = result.scalar_one_or_none()
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # 权限：必须是该班级教师或管理员
    if current_user.role != UserRole.ADMIN and classroom.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == class_id,
            ClassMembership.student_id == student_id,
        )
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise HTTPException(status_code=404, detail="Membership not found")

    membership.is_active = False
    session.add(membership)
    await session.commit()


# --- Announcement Endpoints ---

@router.get("/{class_id}/announcements", response_model=List[AnnouncementRead])
async def list_announcements(
    class_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """班级公告列表，班级成员/教师/管理员可见。"""
    # 权限复用 get_classroom 权限判定
    await get_classroom(class_id, session=session, current_user=current_user)

    stmt = (
        select(Announcement)
        .where(Announcement.class_id == class_id, Announcement.is_active == True)  # noqa: E712
        .order_by(Announcement.is_pinned.desc(), Announcement.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("/{class_id}/announcements", response_model=AnnouncementRead)
async def create_announcement(
    class_id: int,
    announcement_in: AnnouncementCreate,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师/管理员发布公告。"""
    # 仅班主任或管理员
    classroom = await session.get(Classroom, class_id)
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found")
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER) or (
        current_user.role == UserRole.TEACHER and classroom.teacher_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 覆盖 class_id，防止前端篡改
    announcement = Announcement(
        class_id=class_id,
        title=announcement_in.title,
        content=announcement_in.content,
        is_pinned=announcement_in.is_pinned,
        is_active=announcement_in.is_active,
        created_by=current_user.id,
    )
    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)

    # 为班级成员生成通知
    members_stmt = select(ClassMembership).where(
        ClassMembership.class_id == class_id,
        ClassMembership.is_active == True,  # noqa: E712
    )
    members = (await session.execute(members_stmt)).scalars().all()
    notifications = []
    for m in members:
        notifications.append(
            Notification(
                user_id=m.student_id,
                title=f"班级公告：{announcement.title}",
                content=announcement.content,
                link=f"/classes/{class_id}",
            )
        )
    # 通知班主任本人
    notifications.append(
        Notification(
            user_id=classroom.teacher_id,
            title=f"班级公告（已发布）：{announcement.title}",
            content=announcement.content,
            link=f"/classes/{class_id}",
        )
    )
    session.add_all(notifications)
    await session.commit()
    return announcement


@router.put("/{class_id}/announcements/{announcement_id}", response_model=AnnouncementRead)
async def update_announcement(
    class_id: int,
    announcement_id: int,
    start_update: AnnouncementUpdate,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """教师/管理员更新公告。"""
    classroom = await session.get(Classroom, class_id)
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER) or (
        current_user.role == UserRole.TEACHER and classroom.teacher_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    announcement = await session.get(Announcement, announcement_id)
    if not announcement or announcement.class_id != class_id:
        raise HTTPException(status_code=404, detail="Announcement not found")

    update_data = start_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)

    session.add(announcement)
    await session.commit()
    await session.refresh(announcement)
    return announcement


@router.delete("/{class_id}/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    class_id: int,
    announcement_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> None:
    """教师/管理员删除公告。"""
    classroom = await session.get(Classroom, class_id)
    if classroom is None:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER) or (
        current_user.role == UserRole.TEACHER and classroom.teacher_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    announcement = await session.get(Announcement, announcement_id)
    if not announcement or announcement.class_id != class_id:
        raise HTTPException(status_code=404, detail="Announcement not found")

    await session.delete(announcement)
    await session.commit()
