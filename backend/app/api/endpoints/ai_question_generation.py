from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.ai.pipeline.generate import regenerate_single_draft, run_generation_job
from app.ai.pipeline.publish import draft_to_problem_payload
from app.api import deps
from app.db.session import get_session
from app.models.ai_question_generation import (
    DraftTeacherAction,
    QuestionDraft,
    QuestionGenerationJob,
    QuestionGenerationStatus,
    QuestionValidationRun,
)
from app.models.assignment import Assignment, Problem
from app.models.classroom import Classroom
from app.models.user import User, UserRole
from app.schemas.ai_question_generation import (
    QuestionDraftRegenerateResponse,
    QuestionGenerationJobCreate,
    QuestionGenerationJobDetail,
    QuestionGenerationJobRead,
    QuestionGenerationPublishRequest,
    QuestionGenerationPublishResponse,
)

router = APIRouter()


async def _ensure_classroom_owner(session: AsyncSession, class_id: int, current_user: User) -> Classroom:
    classroom = await session.get(Classroom, class_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if current_user.role == UserRole.ADMIN:
        return classroom

    if current_user.role == UserRole.TEACHER and classroom.teacher_id == current_user.id:
        return classroom

    raise HTTPException(status_code=403, detail="Not enough permissions")


async def _get_job_or_404(session: AsyncSession, job_id: int) -> QuestionGenerationJob:
    job = await session.get(QuestionGenerationJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Question generation job not found")
    return job


@router.post("/question-generation/jobs", response_model=QuestionGenerationJobRead)
async def create_question_generation_job(
    *,
    session: AsyncSession = Depends(get_session),
    payload: QuestionGenerationJobCreate,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    if current_user.role not in (UserRole.TEACHER, UserRole.ADMIN):
        raise HTTPException(status_code=403, detail="Only teacher or admin can create generation jobs")

    await _ensure_classroom_owner(session, payload.class_id, current_user)

    if payload.assignment_id is not None:
        assignment = await session.get(Assignment, payload.assignment_id)
        if not assignment or assignment.classroom_id != payload.class_id:
            raise HTTPException(status_code=400, detail="Assignment does not belong to the selected classroom")

    job = QuestionGenerationJob(
        teacher_id=current_user.id,
        class_id=payload.class_id,
        assignment_id=payload.assignment_id,
        status=QuestionGenerationStatus.PENDING,
        topic=payload.topic,
        knowledge_points=payload.knowledge_points,
        request_payload=payload.model_dump(),
        retrieval_summary={
            "message": "Job created. Retrieval pipeline not wired yet.",
        },
        blueprint_json={},
        started_at=datetime.utcnow(),
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    try:
        job = await run_generation_job(session, job.id)
    except Exception as exc:
        await session.rollback()
        failed_job = await session.get(QuestionGenerationJob, job.id)
        if failed_job:
            failed_job.status = QuestionGenerationStatus.FAILED
            failed_job.error_message = str(exc)
            failed_job.finished_at = datetime.utcnow()
            session.add(failed_job)
            await session.commit()
        raise HTTPException(status_code=500, detail=f"Question generation failed: {exc}") from exc

    return job


@router.get("/question-generation/jobs/{job_id}", response_model=QuestionGenerationJobDetail)
async def get_question_generation_job(
    job_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    job = await _get_job_or_404(session, job_id)
    await _ensure_classroom_owner(session, job.class_id, current_user)

    drafts_result = await session.execute(
        select(QuestionDraft).where(QuestionDraft.job_id == job_id).order_by(QuestionDraft.draft_index, QuestionDraft.id)
    )
    drafts = drafts_result.scalars().all()

    validations_result = await session.execute(
        select(QuestionValidationRun)
        .join(QuestionDraft, QuestionValidationRun.draft_id == QuestionDraft.id)
        .where(QuestionDraft.job_id == job_id)
        .order_by(QuestionValidationRun.created_at.desc())
    )
    validations = validations_result.scalars().all()

    return QuestionGenerationJobDetail(
        **job.model_dump(),
        drafts=drafts,
        validations=validations,
    )


@router.post("/question-generation/jobs/{job_id}/drafts/{draft_id}/regenerate", response_model=QuestionDraftRegenerateResponse)
async def regenerate_question_draft(
    job_id: int,
    draft_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    job = await _get_job_or_404(session, job_id)
    await _ensure_classroom_owner(session, job.class_id, current_user)

    draft = await session.get(QuestionDraft, draft_id)
    if not draft or draft.job_id != job_id:
        raise HTTPException(status_code=404, detail="Draft not found")

    draft = await regenerate_single_draft(session, job_id=job_id, draft_id=draft_id)

    return QuestionDraftRegenerateResponse(
        message="Draft regenerated successfully",
        draft=draft,
    )


@router.post("/question-generation/jobs/{job_id}/publish", response_model=QuestionGenerationPublishResponse)
async def publish_question_generation_job(
    job_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    payload: QuestionGenerationPublishRequest,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    job = await _get_job_or_404(session, job_id)
    classroom = await _ensure_classroom_owner(session, job.class_id, current_user)

    assignment = await session.get(Assignment, payload.assignment_id)
    if not assignment or assignment.classroom_id != classroom.id:
        raise HTTPException(status_code=400, detail="Assignment does not belong to the selected classroom")

    drafts_result = await session.execute(
        select(QuestionDraft)
        .where(
            QuestionDraft.job_id == job_id,
            QuestionDraft.id.in_(payload.accepted_draft_ids),
        )
        .order_by(QuestionDraft.draft_index, QuestionDraft.id)
    )
    drafts = drafts_result.scalars().all()
    if len(drafts) != len(payload.accepted_draft_ids):
        raise HTTPException(status_code=400, detail="Some accepted drafts do not belong to this job")

    already_published = [draft.id for draft in drafts if draft.published_problem_id is not None]
    if already_published:
        raise HTTPException(status_code=400, detail=f"Some drafts have already been published: {already_published}")

    max_order_stmt = select(func.max(Problem.display_order)).where(Problem.assignment_id == assignment.id)
    max_order = (await session.execute(max_order_stmt)).scalar_one_or_none()
    next_order = (max_order or -1) + 1

    created_problem_ids: list[int] = []
    for draft in drafts:
        problem_payload = draft_to_problem_payload(draft, next_order)
        next_order += 1
        problem = Problem(**problem_payload, assignment_id=assignment.id)
        session.add(problem)
        await session.flush()

        draft.teacher_action = DraftTeacherAction.ACCEPTED
        draft.published_problem_id = problem.id
        draft.updated_at = datetime.utcnow()
        session.add(draft)

        created_problem_ids.append(problem.id)

    job.assignment_id = assignment.id
    job.status = QuestionGenerationStatus.PUBLISHED
    job.finished_at = datetime.utcnow()
    session.add(job)
    await session.commit()

    return QuestionGenerationPublishResponse(
        created_problem_ids=created_problem_ids,
        message="Drafts published to assignment successfully",
    )