from datetime import datetime
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.ai.retrieval.ingest import delete_knowledge_document, upsert_knowledge_document, upsert_material_knowledge_document
from app.api import deps
from app.db.session import get_session
from app.models.ai_question_generation import (
    KnowledgeChunk,
    KnowledgeDocument,
    KnowledgeParseStatus,
    KnowledgeSourceType,
)
from app.models.classroom import Classroom
from app.models.material import Material
from app.models.user import User, UserRole
from app.schemas.ai_question_generation import (
    KnowledgeDocumentListResponse,
    KnowledgeDocumentRead,
    KnowledgeSearchResponse,
)

router = APIRouter()


def _ensure_admin(current_user: User) -> None:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can manage public knowledge base")


async def _generate_admin_source_id(session: AsyncSession) -> int:
    max_int32 = 2_147_483_647

    for _ in range(10):
        candidate = (uuid.uuid4().int % (max_int32 - 1)) + 1
        existing = await session.execute(
            select(KnowledgeDocument.id).where(
                KnowledgeDocument.source_type == KnowledgeSourceType.ADMIN_MATERIAL,
                KnowledgeDocument.source_id == candidate,
            )
        )
        if existing.scalar_one_or_none() is None:
            return candidate

    raise HTTPException(status_code=500, detail="Failed to allocate source id for admin knowledge document")


async def _ensure_material_ingest_permission(session: AsyncSession, material: Material, current_user: User) -> Classroom:
    classroom = await session.get(Classroom, material.class_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if current_user.role == UserRole.ADMIN:
        return classroom

    if current_user.role == UserRole.TEACHER and classroom.teacher_id == current_user.id:
        return classroom

    raise HTTPException(status_code=403, detail="Not enough permissions")


@router.post("/materials/{material_id}/ingest", response_model=KnowledgeDocumentRead)
async def ingest_material_to_knowledge_base(
    material_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    material = await session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    classroom = await _ensure_material_ingest_permission(session, material, current_user)

    document = await upsert_material_knowledge_document(
        session,
        material=material,
        teacher_id=classroom.teacher_id,
    )
    await session.commit()
    await session.refresh(document)
    return document


@router.get("/admin-materials", response_model=KnowledgeDocumentListResponse)
async def list_admin_knowledge_documents(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    _ensure_admin(current_user)

    limit = max(1, min(limit, 100))
    filters = [KnowledgeDocument.source_type == KnowledgeSourceType.ADMIN_MATERIAL]
    if keyword:
        like = f"%{keyword}%"
        filters.append(KnowledgeDocument.title.ilike(like))

    stmt = select(KnowledgeDocument).where(*filters).order_by(KnowledgeDocument.updated_at.desc())
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()
    result = await session.execute(stmt.offset(skip).limit(limit))
    items = result.scalars().all()
    return KnowledgeDocumentListResponse(items=items, total=total)


@router.post("/admin-materials", response_model=KnowledgeDocumentRead)
async def upload_admin_knowledge_document(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
) -> Any:
    _ensure_admin(current_user)

    admin_dir = Path("uploads/knowledge_base/admin")
    admin_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix or ""
    filename = f"{uuid.uuid4()}{suffix}"
    file_path = admin_dir / filename

    try:
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())

        file_url = f"/static/knowledge_base/admin/{filename}"
        source_id = await _generate_admin_source_id(session)
        document = await upsert_knowledge_document(
            session,
            source_type=KnowledgeSourceType.ADMIN_MATERIAL,
            source_id=source_id,
            class_id=None,
            owner_id=current_user.id,
            title=title,
            description=description,
            file_url=file_url,
            file_type=(Path(file.filename or "").suffix.lstrip(".") or (file.content_type or "other")).lower(),
            extra_metadata={
                "description": description,
                "file_url": file_url,
                "original_filename": file.filename,
                "uploaded_by": current_user.id,
            },
        )
        if document.parse_status != KnowledgeParseStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=document.parse_error or "Automatic knowledge ingestion failed")

        await session.commit()
        await session.refresh(document)
        return document
    except HTTPException:
        await session.rollback()
        if file_path.exists():
            file_path.unlink()
        raise
    except Exception as exc:
        await session.rollback()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Admin knowledge upload failed: {exc}") from exc


@router.delete("/admin-materials/{document_id}", response_model=KnowledgeDocumentRead)
async def delete_admin_knowledge_document(
    document_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    _ensure_admin(current_user)

    document = await session.get(KnowledgeDocument, document_id)
    if not document or document.source_type != KnowledgeSourceType.ADMIN_MATERIAL:
        raise HTTPException(status_code=404, detail="Knowledge document not found")

    file_path = Path(document.file_path) if document.file_path else None
    try:
        await delete_knowledge_document(session, document_id=document.id)
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    if file_path and file_path.exists():
        try:
            file_path.unlink()
        except Exception:
            pass

    return document


@router.get("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge_chunks(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    q: str,
    class_id: Optional[int] = None,
    source_type: Optional[KnowledgeSourceType] = None,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    limit = max(1, min(limit, 100))
    filters = []
    if class_id is not None:
        filters.append(KnowledgeDocument.class_id == class_id)
    if source_type is not None:
        filters.append(KnowledgeDocument.source_type == source_type)
    if current_user.role != UserRole.ADMIN:
        filters.append(
            (KnowledgeDocument.class_id == None) |  # noqa: E711
            (KnowledgeDocument.teacher_id == current_user.id)
        )

    stmt = (
        select(KnowledgeChunk)
        .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
        .where(KnowledgeChunk.content.ilike(f"%{q}%"), *filters)
        .order_by(KnowledgeChunk.created_at.desc())
    )
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()
    result = await session.execute(stmt.offset(skip).limit(limit))
    items = result.scalars().all()
    return KnowledgeSearchResponse(items=items, total=total)