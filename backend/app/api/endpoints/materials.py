import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.ai.retrieval.ingest import delete_material_knowledge_documents, upsert_material_knowledge_document
from app.api import deps
from app.db.session import get_session
from app.models.ai_question_generation import KnowledgeParseStatus
from app.models.classroom import Classroom, ClassMembership
from app.models.material import Material
from app.models.user import User, UserRole
from app.schemas.material import MaterialListResponse, MaterialRead

router = APIRouter()


async def _ensure_class_access(session: AsyncSession, class_id: int, current_user: User) -> Classroom:
    classroom = await session.get(Classroom, class_id)
    if not classroom or not classroom.is_active:
        raise HTTPException(status_code=404, detail="Classroom not found or inactive")

    if current_user.role == UserRole.ADMIN or classroom.teacher_id == current_user.id:
        return classroom

    # check membership for students
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


def _detect_file_type(upload: UploadFile) -> str:
    content_type = upload.content_type or ""
    filename = upload.filename or ""
    name_lower = filename.lower()
    if "pdf" in content_type or name_lower.endswith(".pdf"):
        return "pdf"
    if "ppt" in content_type or name_lower.endswith(".ppt") or name_lower.endswith(".pptx"):
        return "ppt"
    if content_type.startswith("video/"):
        return "video"
    return "other"


@router.get("/", response_model=MaterialListResponse)
async def list_materials(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    class_id: int,
    file_type: Optional[str] = None,
    keyword: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Any:
    await _ensure_class_access(session, class_id, current_user)

    limit = max(1, min(limit, 100))

    filters = [Material.class_id == class_id]
    if file_type:
        filters.append(Material.file_type == file_type)
    if keyword:
        like = f"%{keyword}%"
        filters.append((Material.title.ilike(like)) | (Material.description.ilike(like)))

    base_stmt = select(Material).where(*filters)
    count_stmt = select(func.count()).select_from(base_stmt.subquery())

    total_result = await session.execute(count_stmt)
    total = total_result.scalar_one()

    stmt = base_stmt.order_by(Material.created_at.desc()).offset(skip).limit(limit)

    result = await session.execute(stmt)
    materials = result.scalars().all()
    return MaterialListResponse(
        items=[MaterialRead.model_validate(m) for m in materials],
        total=total
    )


@router.post("/", response_model=MaterialRead)
async def upload_material(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
    class_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
) -> Any:
    classroom = await _ensure_class_access(session, class_id, current_user)

    # Only teacher of the class or admin can upload
    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        raise HTTPException(status_code=403, detail="Only teacher or admin can upload")
    if current_user.role == UserRole.TEACHER and classroom.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only class teacher can upload")

    materials_dir = Path("uploads/materials") / str(class_id)
    materials_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix or ""
    filename = f"{uuid.uuid4()}{suffix}"
    file_path = materials_dir / filename

    try:
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())

        file_url = f"/static/materials/{class_id}/{filename}"
        file_type = _detect_file_type(file)
        size = file_path.stat().st_size if file_path.exists() else None

        material = Material(
            title=title,
            description=description,
            class_id=class_id,
            file_url=file_url,
            file_type=file_type,
            size=size,
            uploader_id=current_user.id,
        )
        session.add(material)
        await session.flush()

        document = await upsert_material_knowledge_document(
            session,
            material=material,
            teacher_id=classroom.teacher_id,
        )
        if document.parse_status != KnowledgeParseStatus.COMPLETED:
            raise HTTPException(status_code=400, detail=document.parse_error or "Automatic knowledge ingestion failed")

        await session.commit()
        await session.refresh(material)
        return material
    except HTTPException:
        await session.rollback()
        if file_path.exists():
            file_path.unlink()
        raise
    except Exception as exc:
        await session.rollback()
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Material upload failed because automatic knowledge ingestion failed: {exc}") from exc


@router.delete("/{material_id}", response_model=MaterialRead)
async def delete_material(
    material_id: int,
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    material = await session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    classroom = await session.get(Classroom, material.class_id)
    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")

    if current_user.role not in (UserRole.ADMIN, UserRole.TEACHER):
        raise HTTPException(status_code=403, detail="Only teacher or admin can delete")
    if current_user.role == UserRole.TEACHER and classroom.teacher_id != current_user.id and material.uploader_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission to delete")

    file_path = Path(material.file_url.replace("/static/", "uploads/"))
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass

    await delete_material_knowledge_documents(session, material_id=material.id)
    await session.delete(material)
    await session.commit()
    return material
