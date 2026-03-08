from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select
from sqlalchemy import desc

from app.api import deps
from app.db.session import get_session
from app.models.classroom import Classroom, ClassMembership
from app.models.user import User, UserRole
from app.models.discussion import (
    DiscussionQuestion,
    DiscussionAnswer,
    QuestionVote,
    AnswerVote,
)
from app.schemas.discussion import (
    DiscussionQuestionCreate,
    DiscussionQuestionRead,
    DiscussionAnswerCreate,
    DiscussionAnswerRead,
    DiscussionQuestionDetail,
    VoteResponse,
    UserBrief,
    DiscussionQuestionListResponse,
)

router = APIRouter()


async def _ensure_class_access(session: AsyncSession, class_id: int, current_user: User) -> Classroom:
    classroom = await session.get(Classroom, class_id)
    if not classroom or not classroom.is_active:
        raise HTTPException(status_code=404, detail="Classroom not found or inactive")

    if current_user.role == UserRole.ADMIN or classroom.teacher_id == current_user.id:
        return classroom

    # check membership
    result = await session.execute(
        select(ClassMembership).where(
            ClassMembership.class_id == class_id,
            ClassMembership.student_id == current_user.id,
            ClassMembership.is_active == True,  # noqa: E712
        )
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return classroom


def _user_brief(u: User) -> UserBrief:
    return UserBrief(id=u.id, username=u.username, role=u.role, avatar_url=u.avatar_url)


async def _get_user_map(session: AsyncSession, user_ids: List[int]) -> Dict[int, User]:
    if not user_ids:
        return {}
    result = await session.execute(select(User).where(User.id.in_(user_ids)))
    return {u.id: u for u in result.scalars().all()}


@router.post("/classes/{class_id}/discussions", response_model=DiscussionQuestionRead)
async def create_question(
    class_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    question_in: DiscussionQuestionCreate,
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    question = DiscussionQuestion(
        class_id=class_id,
        user_id=current_user.id,
        title=question_in.title,
        content=question_in.content,
    )
    session.add(question)
    await session.commit()
    await session.refresh(question)

    return DiscussionQuestionRead(
        id=question.id,
        class_id=question.class_id,
        user_id=question.user_id,
        title=question.title,
        content=question.content,
        upvote_count=question.upvote_count,
        accepted_answer_id=question.accepted_answer_id,
        is_locked=question.is_locked,
        created_at=question.created_at,
        updated_at=question.updated_at,
        author=_user_brief(current_user),
        answer_count=0,
    )


@router.get("/classes/{class_id}/discussions", response_model=DiscussionQuestionListResponse)
async def list_questions(
    class_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: str = "latest",
    skip: int = 0,
    limit: int = 20,
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    limit = max(1, min(limit, 100))

    filters = [DiscussionQuestion.class_id == class_id]
    if keyword:
        like = f"%{keyword}%"
        filters.append((DiscussionQuestion.title.ilike(like)) | (DiscussionQuestion.content.ilike(like)))

    base_stmt = (
        select(DiscussionQuestion, func.count(DiscussionAnswer.id).label("answer_count"))
        .outerjoin(DiscussionAnswer, DiscussionAnswer.question_id == DiscussionQuestion.id)
        .where(*filters)
        .group_by(DiscussionQuestion.id)
    )

    if status == "answered":
        base_stmt = base_stmt.having(func.count(DiscussionAnswer.id) > 0)
    elif status == "unanswered":
        base_stmt = base_stmt.having(func.count(DiscussionAnswer.id) == 0)
    elif status == "accepted":
        base_stmt = base_stmt.having(func.count(DiscussionAnswer.id) > 0).where(DiscussionQuestion.accepted_answer_id.isnot(None))

    if sort_by == "votes":
        base_stmt = base_stmt.order_by(desc(DiscussionQuestion.upvote_count), desc(DiscussionQuestion.created_at))
    elif sort_by == "answers":
        base_stmt = base_stmt.order_by(desc(func.count(DiscussionAnswer.id)), desc(DiscussionQuestion.created_at))
    else:
        base_stmt = base_stmt.order_by(desc(DiscussionQuestion.created_at))

    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    stmt = base_stmt.offset(skip).limit(limit)
    result = await session.execute(stmt)
    rows = result.all()
    questions = [row[0] for row in rows]
    answer_counts = {row[0].id: row[1] for row in rows}

    user_map = await _get_user_map(session, [q.user_id for q in questions])
    return DiscussionQuestionListResponse(
        items=[
            DiscussionQuestionRead(
                id=q.id,
                class_id=q.class_id,
                user_id=q.user_id,
                title=q.title,
                content=q.content,
                upvote_count=q.upvote_count,
                accepted_answer_id=q.accepted_answer_id,
                is_locked=q.is_locked,
                created_at=q.created_at,
                updated_at=q.updated_at,
                author=_user_brief(user_map[q.user_id]) if q.user_id in user_map else None,
                answer_count=answer_counts.get(q.id, 0),
            )
            for q in questions
        ],
        total=total,
    )


@router.get("/classes/{class_id}/discussions/{question_id}", response_model=DiscussionQuestionDetail)
async def get_question_detail(
    class_id: int,
    question_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    question = await session.get(DiscussionQuestion, question_id)
    if not question or question.class_id != class_id:
        raise HTTPException(status_code=404, detail="Question not found")

    answers_result = await session.execute(
        select(DiscussionAnswer)
        .where(DiscussionAnswer.question_id == question_id)
        .order_by(desc(DiscussionAnswer.created_at))
    )
    answers = answers_result.scalars().all()

    user_ids = [question.user_id] + [a.user_id for a in answers]
    user_map = await _get_user_map(session, user_ids)

    detail = DiscussionQuestionDetail(
        id=question.id,
        class_id=question.class_id,
        user_id=question.user_id,
        title=question.title,
        content=question.content,
        upvote_count=question.upvote_count,
        accepted_answer_id=question.accepted_answer_id,
        is_locked=question.is_locked,
        created_at=question.created_at,
        updated_at=question.updated_at,
        author=_user_brief(user_map[question.user_id]) if question.user_id in user_map else None,
        answer_count=len(answers),
        answers=[
            DiscussionAnswerRead(
                id=a.id,
                question_id=a.question_id,
                user_id=a.user_id,
                content=a.content,
                upvote_count=a.upvote_count,
                is_accepted=a.is_accepted,
                created_at=a.created_at,
                updated_at=a.updated_at,
                author=_user_brief(user_map[a.user_id]) if a.user_id in user_map else None,
            )
            for a in answers
        ],
    )
    return detail


@router.post("/classes/{class_id}/discussions/{question_id}/answers", response_model=DiscussionAnswerRead)
async def create_answer(
    class_id: int,
    question_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    answer_in: DiscussionAnswerCreate,
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    if current_user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Only teacher or admin can answer")

    question = await session.get(DiscussionQuestion, question_id)
    if not question or question.class_id != class_id:
        raise HTTPException(status_code=404, detail="Question not found")

    answer = DiscussionAnswer(
        question_id=question_id,
        user_id=current_user.id,
        content=answer_in.content,
    )
    session.add(answer)
    question.updated_at = answer.created_at
    await session.commit()
    await session.refresh(answer)

    return DiscussionAnswerRead(
        id=answer.id,
        question_id=answer.question_id,
        user_id=answer.user_id,
        content=answer.content,
        upvote_count=answer.upvote_count,
        is_accepted=answer.is_accepted,
        created_at=answer.created_at,
        updated_at=answer.updated_at,
        author=_user_brief(current_user),
    )


@router.post("/classes/{class_id}/discussions/{question_id}/accept/{answer_id}", response_model=DiscussionQuestionDetail)
async def accept_answer(
    class_id: int,
    question_id: int,
    answer_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    question = await session.get(DiscussionQuestion, question_id)
    if not question or question.class_id != class_id:
        raise HTTPException(status_code=404, detail="Question not found")

    # 权限：提问者、任课教师、管理员
    if current_user.id != question.user_id and current_user.role not in (UserRole.ADMIN,) and current_user.id != (await session.get(Classroom, class_id)).teacher_id:
        raise HTTPException(status_code=403, detail="Not allowed to accept answer")

    answer = await session.get(DiscussionAnswer, answer_id)
    if not answer or answer.question_id != question_id:
        raise HTTPException(status_code=404, detail="Answer not found")

    # reset previous accepted if exists
    if question.accepted_answer_id and question.accepted_answer_id != answer_id:
        prev = await session.get(DiscussionAnswer, question.accepted_answer_id)
        if prev:
            prev.is_accepted = False
            session.add(prev)

    question.accepted_answer_id = answer_id
    question.updated_at = answer.updated_at
    answer.is_accepted = True
    session.add(question)
    session.add(answer)
    await session.commit()

    return await get_question_detail(class_id, question_id, session=session, current_user=current_user)


@router.post("/classes/{class_id}/discussions/{question_id}/upvote", response_model=VoteResponse)
async def toggle_question_upvote(
    class_id: int,
    question_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    question = await session.get(DiscussionQuestion, question_id)
    if not question or question.class_id != class_id:
        raise HTTPException(status_code=404, detail="Question not found")

    result = await session.execute(
        select(QuestionVote).where(
            QuestionVote.question_id == question_id,
            QuestionVote.user_id == current_user.id,
        )
    )
    vote = result.scalar_one_or_none()
    user_voted = False

    if vote:
        await session.delete(vote)
        question.upvote_count = max(0, question.upvote_count - 1)
    else:
        vote = QuestionVote(question_id=question_id, user_id=current_user.id)
        session.add(vote)
        question.upvote_count += 1
        user_voted = True

    session.add(question)
    await session.commit()

    return VoteResponse(target_id=question_id, upvote_count=question.upvote_count, user_voted=user_voted)


@router.post("/classes/{class_id}/discussions/{question_id}/answers/{answer_id}/upvote", response_model=VoteResponse)
async def toggle_answer_upvote(
    class_id: int,
    question_id: int,
    answer_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    answer = await session.get(DiscussionAnswer, answer_id)
    if not answer or answer.question_id != question_id:
        raise HTTPException(status_code=404, detail="Answer not found")

    result = await session.execute(
        select(AnswerVote).where(
            AnswerVote.answer_id == answer_id,
            AnswerVote.user_id == current_user.id,
        )
    )
    vote = result.scalar_one_or_none()
    user_voted = False

    if vote:
        await session.delete(vote)
        answer.upvote_count = max(0, answer.upvote_count - 1)
    else:
        vote = AnswerVote(answer_id=answer_id, user_id=current_user.id)
        session.add(vote)
        answer.upvote_count += 1
        user_voted = True

    session.add(answer)
    await session.commit()

    return VoteResponse(target_id=answer_id, upvote_count=answer.upvote_count, user_voted=user_voted)
