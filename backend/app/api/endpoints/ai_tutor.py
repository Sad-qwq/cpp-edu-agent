from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import delete, func, select

from app.ai.tutor.service import (
    append_conversation,
    build_practice_recommendations,
    create_tutor_session,
    ensure_class_access,
    ensure_session_access,
    generate_tutor_reply,
    get_session_detail,
)
from app.api import deps
from app.db.session import get_session as get_db_session
from app.models.ai_tutor import TutorMessage, TutorSession, TutorMode
from app.models.assignment import Problem
from app.models.user import User, UserRole
from app.schemas.ai_tutor import (
    PracticeRecommendationListResponse,
    TutorCodeReviewRequest,
    TutorHintRequest,
    TutorMessageCreate,
    TutorMessageRead,
    TutorReplyPayload,
    TutorSessionCreate,
    TutorSessionDetail,
    TutorSessionListResponse,
)

router = APIRouter()


def _build_session_detail_response(tutor_session: TutorSession, messages: list[Any]) -> TutorSessionDetail:
    return TutorSessionDetail(
        **tutor_session.model_dump(),
        messages=[TutorMessageRead.model_validate(message, from_attributes=True) for message in messages],
    )


@router.post("/sessions", response_model=TutorSessionDetail)
async def create_session(
    *,
    session: AsyncSession = Depends(get_db_session),
    payload: TutorSessionCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await ensure_class_access(session, payload.class_id, current_user)
    student_id = current_user.id
    if current_user.role in (UserRole.ADMIN, UserRole.TEACHER) and student_id is None:
        raise HTTPException(status_code=400, detail="Invalid user")

    tutor_session = await create_tutor_session(
        session,
        class_id=payload.class_id,
        student_id=student_id,
        mode=payload.mode,
        title=payload.title,
        assignment_id=payload.assignment_id,
        problem_id=payload.problem_id,
    )
    await session.commit()
    await session.refresh(tutor_session)

    if payload.initial_question:
        await append_conversation(
            session,
            tutor_session=tutor_session,
            content=payload.initial_question,
        )
        tutor_session = await session.get(TutorSession, tutor_session.id)

    detailed, messages = await get_session_detail(session, tutor_session)
    return _build_session_detail_response(detailed, messages)


@router.get("/sessions", response_model=TutorSessionListResponse)
async def list_tutor_sessions(
    *,
    class_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 50,
) -> Any:
    await ensure_class_access(session, class_id, current_user)

    limit = max(1, min(limit, 100))
    stmt = select(TutorSession).where(TutorSession.class_id == class_id)
    if current_user.role == UserRole.STUDENT:
        stmt = stmt.where(TutorSession.student_id == current_user.id)

    stmt = stmt.order_by(TutorSession.updated_at.desc())
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = int((await session.execute(count_stmt)).scalar_one() or 0)
    result = await session.execute(stmt.offset(skip).limit(limit))
    items = result.scalars().all()
    return TutorSessionListResponse(items=items, total=total)


@router.get("/sessions/{session_id}", response_model=TutorSessionDetail)
async def get_tutor_session(
    session_id: int,
    *,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    tutor_session = await session.get(TutorSession, session_id)
    if not tutor_session:
        raise HTTPException(status_code=404, detail="Tutor session not found")

    await ensure_session_access(session, tutor_session, current_user)
    detailed, messages = await get_session_detail(session, tutor_session)
    return _build_session_detail_response(detailed, messages)


@router.post("/sessions/{session_id}/messages", response_model=TutorSessionDetail)
async def post_message(
    session_id: int,
    *,
    session: AsyncSession = Depends(get_db_session),
    payload: TutorMessageCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    tutor_session = await session.get(TutorSession, session_id)
    if not tutor_session:
        raise HTTPException(status_code=404, detail="Tutor session not found")

    await ensure_session_access(session, tutor_session, current_user)
    await append_conversation(
        session,
        tutor_session=tutor_session,
        content=payload.content,
        hint_level=payload.hint_level,
        student_answer=payload.student_answer,
        student_code=payload.current_code,
        compiler_output=payload.compiler_output,
        expected_output=payload.expected_output,
    )
    refreshed = await session.get(TutorSession, session_id)
    detailed, messages = await get_session_detail(session, refreshed)
    return _build_session_detail_response(detailed, messages)


@router.delete("/sessions/{session_id}")
async def delete_tutor_session(
    session_id: int,
    *,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    tutor_session = await session.get(TutorSession, session_id)
    if not tutor_session:
        raise HTTPException(status_code=404, detail="Tutor session not found")

    await ensure_session_access(session, tutor_session, current_user)
    await session.execute(delete(TutorMessage).where(TutorMessage.session_id == session_id))
    await session.delete(tutor_session)
    await session.commit()
    return {"message": "Tutor session deleted"}


@router.post("/problems/{problem_id}/hint", response_model=TutorReplyPayload)
async def get_problem_hint(
    problem_id: int,
    *,
    session: AsyncSession = Depends(get_db_session),
    payload: TutorHintRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await ensure_class_access(session, payload.class_id, current_user)

    problem = await session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    return await generate_tutor_reply(
        session,
        class_id=payload.class_id,
        mode=TutorMode.HINT,
        question=f"请针对当前题目给我第 {payload.hint_level} 层提示，不要直接给完整答案。",
        hint_level=payload.hint_level,
        assignment_id=payload.assignment_id,
        problem_id=problem_id,
        student_answer=payload.student_answer,
        student_code=payload.current_code,
    )


@router.post("/code-review", response_model=TutorReplyPayload)
async def code_review(
    *,
    session: AsyncSession = Depends(get_db_session),
    payload: TutorCodeReviewRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await ensure_class_access(session, payload.class_id, current_user)
    return await generate_tutor_reply(
        session,
        class_id=payload.class_id,
        mode=TutorMode.CODE_REVIEW,
        question=payload.student_question or "请帮我解释这段代码的问题，并告诉我下一步该如何修改。",
        assignment_id=payload.assignment_id,
        problem_id=payload.problem_id,
        student_code=payload.code,
        compiler_output=payload.compiler_output,
        expected_output=payload.expected_output,
    )


@router.get("/students/{student_id}/recommendations", response_model=PracticeRecommendationListResponse)
async def get_practice_recommendations(
    student_id: int,
    *,
    class_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await ensure_class_access(session, class_id, current_user)
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="Students can only view their own recommendations")

    items = await build_practice_recommendations(session, class_id=class_id, student_id=student_id)
    return PracticeRecommendationListResponse(items=items)
