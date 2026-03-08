from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ModelConfigRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    provider: str
    model_name: str
    temperature: float
    max_tokens: int
    rate_limit_per_minute: int
    daily_quota: Optional[int]
    updated_at: datetime


class ModelConfigUpdate(BaseModel):
    provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    rate_limit_per_minute: Optional[int] = Field(default=None, gt=0)
    daily_quota: Optional[int] = Field(default=None, gt=0)


class ModelUsageLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: Optional[float]
    created_at: datetime


class ModelUsageLogListResponse(BaseModel):
    items: List[ModelUsageLogRead]
    total: int
