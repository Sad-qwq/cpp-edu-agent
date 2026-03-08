from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import func, select

from app.api import deps
from app.db.session import get_session
from app.models.model_config import ModelConfig, ModelUsageLog
from app.models.user import User
from app.schemas.model_config import (
    ModelConfigRead,
    ModelConfigUpdate,
    ModelUsageLogListResponse,
    ModelUsageLogRead,
)

router = APIRouter()


async def _get_or_create_config(session: AsyncSession) -> ModelConfig:
    config = await session.get(ModelConfig, 1)
    if config:
        return config
    config = ModelConfig()
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config


@router.get("/config", response_model=ModelConfigRead)
async def get_model_config(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
) -> Any:
    config = await _get_or_create_config(session)
    return config


@router.put("/config", response_model=ModelConfigRead)
async def update_model_config(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
    payload: ModelConfigUpdate,
) -> Any:
    config = await _get_or_create_config(session)
    update_data = payload.dict(exclude_unset=True)
    if not update_data:
        return config
    for field, value in update_data.items():
        setattr(config, field, value)
    config.updated_at = datetime.utcnow()
    session.add(config)
    await session.commit()
    await session.refresh(config)
    return config


@router.get("/logs", response_model=ModelUsageLogListResponse)
async def list_usage_logs(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
    user_id: Optional[int] = None,
    model_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    limit = max(1, min(limit, 200))
    filters = []
    if user_id is not None:
        filters.append(ModelUsageLog.user_id == user_id)
    if model_name:
        filters.append(ModelUsageLog.model_name == model_name)

    base_stmt = select(ModelUsageLog).where(*filters).order_by(ModelUsageLog.created_at.desc())
    count_stmt = select(func.count()).select_from(base_stmt.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    result = await session.execute(base_stmt.offset(skip).limit(limit))
    items = result.scalars().all()
    return ModelUsageLogListResponse(
        items=[
          ModelUsageLogRead(
            id=i.id,
            user_id=i.user_id,
            model_name=i.model_name,
            prompt_tokens=i.prompt_tokens,
            completion_tokens=i.completion_tokens,
            total_tokens=i.total_tokens,
            cost=i.cost,
            created_at=i.created_at,
          ) for i in items
        ],
        total=total,
    )


@router.post("/logs/record", response_model=ModelUsageLogRead)
async def record_usage_log(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(deps.get_current_admin),
    log: ModelUsageLogRead,
) -> Any:
    new_log = ModelUsageLog(
        user_id=log.user_id,
        model_name=log.model_name,
        prompt_tokens=log.prompt_tokens,
        completion_tokens=log.completion_tokens,
        total_tokens=log.total_tokens,
        cost=log.cost,
    )
    session.add(new_log)
    await session.commit()
    await session.refresh(new_log)
    return new_log
