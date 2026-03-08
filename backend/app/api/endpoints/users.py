
from datetime import datetime
from typing import Any, List, Optional
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import func, desc, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash, verify_password


from app.api import deps
from app.db.session import get_session
from app.models.user import User, UserRole
from app.models.classroom import Classroom, ClassMembership
from app.models.assignment import Assignment, Submission
from app.schemas.user import UserRead, UserUpdate, UserUpdateMe, UserChangePassword

router = APIRouter()


class DashboardActivity(BaseModel):
    id: int
    content: str
    time: datetime
    type: str  # "submission", "assignment", "join"


class DashboardStats(BaseModel):
    role: str
    class_count: int
    assignment_count: int  # Student: upcoming; Teacher: total created
    submission_count: int  # Student: my submissions; Teacher: total received
    recent_activities: List[DashboardActivity]


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """获取用户仪表盘统计数据"""
    
    activities = []
    
    if current_user.role == UserRole.STUDENT:
        # 1. Class Count
        res_classes = await session.execute(
            select(func.count()).select_from(ClassMembership)
            .where(ClassMembership.student_id == current_user.id, ClassMembership.is_active == True) # noqa: E712
        )
        class_count = res_classes.scalar() or 0

        # 2. Upcoming Assignments (in my classes, due date > now or none)
        # First get my class IDs
        res_my_classes = await session.execute(
           select(ClassMembership.class_id)
           .where(ClassMembership.student_id == current_user.id, ClassMembership.is_active == True) # noqa: E712
        )
        my_class_ids = res_my_classes.scalars().all()
        
        assignment_count = 0
        if my_class_ids:
            now = datetime.utcnow()
            res_assigns = await session.execute(
                select(func.count()).select_from(Assignment)
                .where(
                    Assignment.classroom_id.in_(my_class_ids),
                    or_(Assignment.due_date >= now, Assignment.due_date == None) # noqa: E711
                )
            )
            assignment_count = res_assigns.scalar() or 0

        # 3. My Submissions
        res_subs = await session.execute(
            select(func.count()).select_from(Submission)
            .where(Submission.student_id == current_user.id)
        )
        submission_count = res_subs.scalar() or 0
        
        # 4. Recent Activities (My recent submissions)
        res_act = await session.execute(
            select(Submission, Assignment).join(Assignment)
            .where(Submission.student_id == current_user.id)
            .order_by(desc(Submission.submitted_at))
            .limit(5)
        )
        rows = res_act.all()
        for sub, assign in rows:
            activities.append(DashboardActivity(
                id=sub.id,
                content=f"提交了作业: {assign.title}",
                time=sub.submitted_at,
                type="submission"
            ))

    elif current_user.role in [UserRole.TEACHER, UserRole.ADMIN]:
        # 1. Teaching Class Count
        stmt_class = select(func.count()).select_from(Classroom)
        if current_user.role == UserRole.TEACHER:
            stmt_class = stmt_class.where(Classroom.teacher_id == current_user.id)
        
        res_classes = await session.execute(stmt_class)
        class_count = res_classes.scalar() or 0

        # 2. Created Assignments
        stmt_assign = select(func.count()).select_from(Assignment)
        if current_user.role == UserRole.TEACHER:
            # Need to join Classroom to filter by teacher_id?
            # Or get all classroom IDs first.
            # Efficient way:
            stmt_assign = stmt_assign.join(Classroom).where(Classroom.teacher_id == current_user.id)
        
        res_assigns = await session.execute(stmt_assign)
        assignment_count = res_assigns.scalar() or 0

        # 3. Received Submissions (for my assignments)
        stmt_subs = select(func.count()).select_from(Submission).join(Assignment).join(Classroom)
        if current_user.role == UserRole.TEACHER:
            stmt_subs = stmt_subs.where(Classroom.teacher_id == current_user.id)
            
        res_subs = await session.execute(stmt_subs)
        submission_count = res_subs.scalar() or 0

        # 4. Recent Activities (Recent submissions to my classes)
        stmt_act = select(Submission, Assignment, User)\
            .join(Assignment).join(Classroom).join(User, Submission.student_id == User.id)
            
        if current_user.role == UserRole.TEACHER:
            stmt_act = stmt_act.where(Classroom.teacher_id == current_user.id)
            
        stmt_act = stmt_act.order_by(desc(Submission.submitted_at)).limit(5)
        
        res_act = await session.execute(stmt_act)
        rows = res_act.all()
        for sub, assign, student in rows:
            activities.append(DashboardActivity(
                id=sub.id,
                content=f"{student.username} 提交了: {assign.title}",
                time=sub.submitted_at,
                type="submission"
            ))
            
    else:
         class_count = 0
         assignment_count = 0
         submission_count = 0

    return DashboardStats(
        role=current_user.role,
        class_count=class_count,
        assignment_count=assignment_count,
        submission_count=submission_count,
        recent_activities=activities
    )


@router.get("/me", response_model=UserRead)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取当前登录用户信息
    """
    return current_user


@router.put("/me", response_model=UserRead)
async def update_user_me(
    *,
    session: AsyncSession = Depends(get_session),
    user_in: UserUpdateMe,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """用户更新个人信息"""
    if user_in.username:
        # Check uniqueness if username changed
        result = await session.execute(select(User).where(User.username == user_in.username))
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )
        current_user.username = user_in.username
    if user_in.bio is not None:
        current_user.bio = user_in.bio
    if user_in.avatar_url is not None:
        current_user.avatar_url = user_in.avatar_url

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)
    return current_user


@router.post("/me/password", response_model=Any)
async def change_password(
    *,
    session: AsyncSession = Depends(get_session),
    password_in: UserChangePassword,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """修改密码"""
    if not verify_password(password_in.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    if password_in.old_password == password_in.new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as old password")
        
    current_user.hashed_password = get_password_hash(password_in.new_password)
    session.add(current_user)
    await session.commit()
    return {"msg": "Password updated successfully"}


@router.post("/me/avatar", response_model=Any)
async def upload_avatar(
    *,
    session: AsyncSession = Depends(get_session),
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """上传头像"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Ensure upload directory exists
    upload_dir = Path("uploads/avatars")
    if not upload_dir.exists():
        upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    # Sanitize filename or just use extension
    file_ext = Path(file.filename).suffix if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    avatar_url = f"/static/avatars/{filename}"
    current_user.avatar_url = avatar_url
    session.add(current_user)
    await session.commit()
    
    return {"avatar_url": avatar_url}

@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    is_approved: Optional[bool] = None,
    current_user: User = Depends(deps.get_current_admin),  # 仅管理员可查看所有用户
    session: AsyncSession = Depends(get_session),
) -> Any:
    """获取所有用户列表（管理员权限），支持简单筛选。"""
    statement = select(User)

    # 动态增加筛选条件
    if role is not None:
        statement = statement.where(User.role == role)
    if is_active is not None:
        statement = statement.where(User.is_active == is_active)
    if is_approved is not None:
        statement = statement.where(User.is_approved == is_approved)

    statement = statement.offset(skip).limit(limit)
    result = await session.execute(statement)
    users = result.scalars().all()
    return users


@router.get("/pending/teachers", response_model=List[UserRead])
async def list_pending_teachers(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    stmt = (
        select(User)
        .where(User.role == UserRole.TEACHER, User.is_approved == False)  # noqa: E712
        .order_by(User.id.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_admin),
    session: AsyncSession = Depends(get_session),
) -> Any:
    """管理员更新用户信息（角色 / 启用状态 / 审核状态）。"""

    result = await session.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 禁止将管理员账号降级为非管理员（防止误操作导致无管理员）
    if db_user.role == UserRole.ADMIN and user_in.role and user_in.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot demote an admin account",
        )

    # 只允许用户名为 admin 的账号拥有管理员角色，同时禁止管理员账号改名
    target_username = user_in.username if user_in.username is not None else db_user.username
    target_role = user_in.role if user_in.role is not None else db_user.role
    if target_role == UserRole.ADMIN and target_username != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only username 'admin' can have admin role",
        )
    if db_user.role == UserRole.ADMIN and target_username != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin username must remain 'admin'",
        )

    # 根据传入字段有选择地更新
    update_data = user_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/{user_id}/approve-teacher", response_model=UserRead)
async def approve_teacher(
    user_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    db_user = await session.get(User, user_id)
    if not db_user or db_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    db_user.is_approved = True
    db_user.is_active = True
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.post("/{user_id}/reject-teacher", response_model=UserRead)
async def reject_teacher(
    user_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    db_user = await session.get(User, user_id)
    if not db_user or db_user.role != UserRole.TEACHER:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")

    db_user.is_approved = False
    db_user.is_active = False
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user
