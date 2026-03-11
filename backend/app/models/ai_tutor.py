from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class TutorMode(str, Enum):
    CONCEPT = "concept"
    HINT = "hint"
    CODE_REVIEW = "code_review"
    PRACTICE = "practice"


class TutorMessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class TutorSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="classroom.id", index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    assignment_id: Optional[int] = Field(default=None, foreign_key="assignment.id")
    problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    mode: TutorMode = Field(default=TutorMode.CONCEPT)
    title: str = "AI 助学会话"
    latest_summary: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TutorMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="tutorsession.id", index=True)
    role: TutorMessageRole
    content: str = Field(sa_column=Column(Text, nullable=False))
    hint_level: Optional[int] = None
    cited_chunk_ids: List[int] = Field(default=[], sa_column=Column(JSON))
    related_knowledge_points: List[str] = Field(default=[], sa_column=Column(JSON))
    reply_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
