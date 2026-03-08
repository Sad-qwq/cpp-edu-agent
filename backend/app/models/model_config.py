from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ModelConfig(SQLModel, table=True):
    id: Optional[int] = Field(default=1, primary_key=True)
    provider: str = "openai"
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.2
    max_tokens: int = 2048
    rate_limit_per_minute: int = 60
    daily_quota: Optional[int] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ModelUsageLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    model_name: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
