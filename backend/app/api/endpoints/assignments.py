from typing import Any, List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select, Session  # Use AsyncSession if app uses async
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.user import User, UserRole
from app.models.classroom import Classroom, ClassMembership
from app.models.assignment import (
    Assignment, AssignmentCreate, AssignmentRead, AssignmentUpdate,
    Problem, ProblemCreate, ProblemRead, ProblemUpdate,
    Submission, SubmissionCreate, SubmissionRead, SubmissionGrade
)
from app.db.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def _normalize_naive(dt: datetime | None) -> datetime | None:
    """Ensure datetime is naive UTC to satisfy Postgres timestamp columns."""
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).replace(tzinfo=None) if dt.tzinfo else dt


class SubmissionCreatePayload(BaseModel):
    """请求体：只需要提交答案，assignment_id 和 student_id 从路径和 token 推导。"""
    answers: dict[str, Any]


async def _ensure_classroom_permission(
    session: AsyncSession,
    classroom_id: int,
    current_user: User,
    *,
    require_owner: bool = False,
):
    """确保用户有权访问/管理该班级；返回班级对象。"""
    classroom = await session.get(Classroom, classroom_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # 管理员放行
    if current_user.role == UserRole.ADMIN:
        return classroom

    # 教师需为班级负责人
    if current_user.role == UserRole.TEACHER:
        if classroom.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions for this classroom")
        return classroom

    # 学生需为班级成员；如果要求 owner 则学生必定无权限
    if require_owner:
        raise HTTPException(status_code=403, detail="Not enough permissions for this classroom")

    result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == classroom_id,
            ClassMembership.student_id == current_user.id,
            ClassMembership.is_active == True,  # noqa: E712
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this classroom")

    return classroom

# --- Assignment Endpoints ---

@router.post("/", response_model=AssignmentRead)
async def create_assignment(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_in: AssignmentCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Create new assignment. Only for teachers/admins."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    # 教师必须是班级负责人；管理员放行
    await _ensure_classroom_permission(
        session,
        assignment_in.classroom_id,
        current_user,
        require_owner=True,
    )

    # Normalize due_date to naive UTC
    assignment_in.due_date = _normalize_naive(assignment_in.due_date)

    assignment = Assignment.from_orm(assignment_in)
    assignment.due_date = _normalize_naive(assignment.due_date)
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)
    return assignment

@router.get("/", response_model=List[AssignmentRead])
async def read_assignments(
    *,
    session: AsyncSession = Depends(deps.get_session),
    classroom_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Retrieve assignments for a classroom."""
    # 先校验班级访问权限（学生需为成员，教师需为负责人）
    await _ensure_classroom_permission(session, classroom_id, current_user)

    statement = select(Assignment).where(Assignment.classroom_id == classroom_id).offset(skip).limit(limit)
    assignments_result = await session.execute(statement)
    assignments = assignments_result.scalars().all()

    if current_user.role == UserRole.STUDENT and assignments:
        assignment_ids = [a.id for a in assignments]
        sub_stmt = select(Submission).where(
            Submission.assignment_id.in_(assignment_ids),
            Submission.student_id == current_user.id,
        )
        subs_result = await session.execute(sub_stmt)
        subs = {s.assignment_id: s for s in subs_result.scalars().all()}

        enhanced = []
        for a in assignments:
            data = a.dict()
            sub = subs.get(a.id)
            data["my_submitted"] = bool(sub)
            data["my_score"] = sub.score if sub else None
            data["my_submission_id"] = sub.id if sub else None
            enhanced.append(data)
        return enhanced

    return assignments

@router.get("/{assignment_id}", response_model=AssignmentRead)
async def read_assignment(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get assignment by ID."""
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await _ensure_classroom_permission(session, assignment.classroom_id, current_user)
    # Attach current student's submission info if applicable
    if current_user.role == UserRole.STUDENT:
        sub_stmt = select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == current_user.id,
        )
        sub_result = await session.execute(sub_stmt)
        sub = sub_result.scalars().first()
        data = assignment.dict()
        if sub:
            data["my_submitted"] = True
            data["my_score"] = sub.score
            data["my_submission_id"] = sub.id
        else:
            data["my_submitted"] = False
            data["my_score"] = None
            data["my_submission_id"] = None
        return data
    return assignment

@router.put("/{assignment_id}", response_model=AssignmentRead)
async def update_assignment(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    assignment_in: AssignmentUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update assignment."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )

    assignment_data = assignment_in.dict(exclude_unset=True)
    # Normalize due_date to naive UTC if present
    if "due_date" in assignment_data:
        assignment_data["due_date"] = _normalize_naive(assignment_data["due_date"])
    for key, value in assignment_data.items():
        setattr(assignment, key, value)
    assignment.due_date = _normalize_naive(assignment.due_date)
        
    session.add(assignment)
    await session.commit()
    await session.refresh(assignment)
    return assignment

@router.delete("/{assignment_id}", response_model=AssignmentRead)
async def delete_assignment(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete assignment."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )
        
    await session.delete(assignment)
    await session.commit()
    return assignment

# --- Problem Endpoints ---

@router.post("/{assignment_id}/problems", response_model=ProblemRead)
async def create_problem(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    problem_in: ProblemCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Add a problem to an assignment."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
        
    # Check assignment and ownership
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )

    # 直接用提交的数据构造 Problem，并显式设置 assignment_id
    if hasattr(problem_in, "model_dump"):
        problem_data = problem_in.model_dump()
    else:
        problem_data = problem_in.dict()

    problem = Problem(**problem_data, assignment_id=assignment_id)
    session.add(problem)
    await session.commit()
    await session.refresh(problem)
    return problem

@router.get("/{assignment_id}/problems", response_model=List[ProblemRead])
async def read_problems(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get all problems for an assignment."""
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await _ensure_classroom_permission(session, assignment.classroom_id, current_user)

    statement = select(Problem).where(Problem.assignment_id == assignment_id).order_by(Problem.display_order)
    result = await session.execute(statement)
    problems = result.scalars().all()
    return problems


@router.put("/{assignment_id}/problems/{problem_id}", response_model=ProblemRead)
async def update_problem(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    problem_id: int,
    problem_in: ProblemUpdate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Update a problem on an assignment (teacher/admin only)."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )

    problem = await session.get(Problem, problem_id)
    if not problem or problem.assignment_id != assignment_id:
        raise HTTPException(status_code=404, detail="Problem not found")

    update_data = problem_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(problem, key, value)

    session.add(problem)
    await session.commit()
    await session.refresh(problem)
    return problem


@router.delete("/{assignment_id}/problems/{problem_id}", response_model=ProblemRead)
async def delete_problem(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    problem_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete a problem from an assignment (teacher/admin only)."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )

    problem = await session.get(Problem, problem_id)
    if not problem or problem.assignment_id != assignment_id:
        raise HTTPException(status_code=404, detail="Problem not found")

    await session.delete(problem)
    await session.commit()
    return problem

# --- Submission Endpoints ---

@router.post("/{assignment_id}/submit", response_model=SubmissionRead)
async def submit_assignment(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    submission_in: SubmissionCreatePayload,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Submit assignment."""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=403, detail="Only student can submit assignment")
    # Check assignment exists
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    # Student must belong to classroom
    await _ensure_classroom_permission(session, assignment.classroom_id, current_user)
        
    # Check if submission already exists? Or allow multiple?
    # For now, allow multiple, just create new record. Or update existing?
    # Let's check existing submission
    statement = select(Submission).where(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    )
    result = await session.execute(statement)
    existing_submission = result.scalars().first()
    
    if existing_submission:
        # Update existing
        existing_submission.answers = submission_in.answers
        existing_submission.submitted_at = datetime.utcnow() # Update timestamp
        session.add(existing_submission)
        await session.commit()
        await session.refresh(existing_submission)
        return existing_submission
    else:
        # Create new
        submission = Submission(
            assignment_id=assignment_id,
            student_id=current_user.id, # Ensure valid ID from token
            answers=submission_in.answers
        )
        session.add(submission)
        await session.commit()
        await session.refresh(submission)
        return submission

@router.get("/{assignment_id}/submissions/me", response_model=SubmissionRead)
async def read_my_submission(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get my submission."""
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await _ensure_classroom_permission(session, assignment.classroom_id, current_user)

    statement = select(Submission).where(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    )
    result = await session.execute(statement)
    submission = result.scalars().first()
    if not submission:
        # Instead of 404, maybe return null or empty? 
        # But for now 404 is fine if they haven't submitted.
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission

@router.get("/{assignment_id}/submissions", response_model=List[SubmissionRead])
async def read_assignment_submissions(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Get all submissions for an assignment. Teacher only."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )

    statement = (
        select(Submission, User.username)
        .join(User, Submission.student_id == User.id)
        .where(Submission.assignment_id == assignment_id)
        .order_by(Submission.submitted_at.desc())
        .offset(skip)
        .limit(limit)
    )
    results = await session.execute(statement)
    
    submissions = []
    for sub, username in results.all():
        sub_dict = sub.dict()
        sub_dict["student_name"] = username
        submissions.append(sub_dict)
        
    return submissions


@router.put("/{assignment_id}/submissions/{submission_id}", response_model=SubmissionRead)
async def grade_submission(
    *,
    session: AsyncSession = Depends(deps.get_session),
    assignment_id: int,
    submission_id: int,
    grade_in: SubmissionGrade,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """Grade a submission."""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Only teacher can grade")
    assignment = await session.get(Assignment, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await _ensure_classroom_permission(
        session,
        assignment.classroom_id,
        current_user,
        require_owner=True,
    )

    submission = await session.get(Submission, submission_id)
    if not submission or submission.assignment_id != assignment_id:
        raise HTTPException(status_code=404, detail="Submission not found")
        
    submission.score = grade_in.score
    submission.feedback = grade_in.feedback
    
    session.add(submission)
    await session.commit()
    await session.refresh(submission)
    
    # Also fetch student name for response if needed, for consistency
    student = await session.get(User, submission.student_id)
    sub_dict = submission.dict()
    sub_dict["student_name"] = student.username if student else "Unknown"
    
    return sub_dict


