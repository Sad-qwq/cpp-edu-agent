from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.ai_tutor import TutorMessageRole, TutorMode


class TutorReplyPayload(BaseModel):
    answer: str
    hint_level: Optional[int] = None
    cited_chunk_ids: List[int] = Field(default_factory=list)
    related_knowledge_points: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    recommended_action: str = ""
    risk_flags: List[str] = Field(default_factory=list)


class TutorSessionCreate(BaseModel):
    class_id: int
    assignment_id: Optional[int] = None
    problem_id: Optional[int] = None
    mode: TutorMode = TutorMode.CONCEPT
    title: Optional[str] = Field(default=None, max_length=200)
    initial_question: Optional[str] = None


class TutorMessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    hint_level: Optional[int] = Field(default=None, ge=1, le=3)
    student_answer: Optional[str] = None
    current_code: Optional[str] = None
    compiler_output: Optional[str] = None
    expected_output: Optional[str] = None


class TutorHintRequest(BaseModel):
    class_id: int
    assignment_id: Optional[int] = None
    student_answer: Optional[str] = None
    current_code: Optional[str] = None
    hint_level: int = Field(default=1, ge=1, le=3)


class TutorCodeReviewRequest(BaseModel):
    class_id: int
    assignment_id: Optional[int] = None
    problem_id: Optional[int] = None
    code: str = Field(min_length=1)
    compiler_output: Optional[str] = None
    input_data: Optional[str] = None
    expected_output: Optional[str] = None
    student_question: Optional[str] = None


class PracticeRecommendationRead(BaseModel):
    title: str
    reason: str
    target_knowledge_points: List[str] = Field(default_factory=list)
    action_type: str
    assignment_id: Optional[int] = None
    problem_id: Optional[int] = None


class TutorMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    role: TutorMessageRole
    content: str
    hint_level: Optional[int]
    cited_chunk_ids: List[int]
    related_knowledge_points: List[str]
    reply_json: Dict[str, Any]
    created_at: datetime


class TutorSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    class_id: int
    student_id: int
    assignment_id: Optional[int]
    problem_id: Optional[int]
    mode: TutorMode
    title: str
    latest_summary: Optional[str]
    created_at: datetime
    updated_at: datetime


class TutorSessionDetail(TutorSessionRead):
    messages: List[TutorMessageRead] = Field(default_factory=list)


class TutorSessionListResponse(BaseModel):
    items: List[TutorSessionRead]
    total: int


class PracticeRecommendationListResponse(BaseModel):
    items: List[PracticeRecommendationRead]
