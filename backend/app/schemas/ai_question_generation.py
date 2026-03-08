from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.ai_question_generation import (
    DraftTeacherAction,
    DraftValidationStatus,
    KnowledgeParseStatus,
    KnowledgeSourceType,
    QuestionGenerationStatus,
    ValidationType,
)


class KnowledgeDocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: KnowledgeSourceType
    source_id: Optional[int]
    class_id: Optional[int]
    teacher_id: Optional[int]
    title: str
    file_path: Optional[str]
    mime_type: Optional[str]
    parse_status: KnowledgeParseStatus
    parse_error: Optional[str]
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class KnowledgeChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    document_id: int
    chunk_index: int
    content: str
    content_type: str
    token_count: int
    knowledge_tags: List[str]
    metadata_json: Dict[str, Any]
    created_at: datetime


class KnowledgeSearchResponse(BaseModel):
    items: List[KnowledgeChunkRead]
    total: int


class KnowledgeDocumentListResponse(BaseModel):
    items: List[KnowledgeDocumentRead]
    total: int


class QuestionGenerationJobCreate(BaseModel):
    class_id: int
    assignment_id: Optional[int] = None
    topic: str = Field(min_length=1, max_length=200)
    knowledge_points: List[str] = Field(default_factory=list)
    total_count: int = Field(default=5, ge=1, le=20)
    question_type_distribution: Dict[str, int] = Field(default_factory=dict)
    difficulty_distribution: Dict[str, int] = Field(default_factory=dict)
    use_class_materials: bool = True
    use_admin_knowledge_base: bool = True
    use_history_questions: bool = True
    extra_constraints: Optional[str] = None


class QuestionValidationRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    draft_id: int
    validation_type: ValidationType
    status: DraftValidationStatus
    report_json: Dict[str, Any]
    created_at: datetime


class QuestionDraftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    draft_index: int
    type: str
    content: str
    options: List[str]
    correct_answer: Optional[str]
    code_template: Optional[str]
    test_cases: List[Dict[str, str]]
    reference_solution: Optional[str]
    explanation: Optional[str]
    target_knowledge_points: List[str]
    difficulty: Optional[str]
    estimated_score: Optional[int]
    source_chunk_ids: List[int]
    validation_status: DraftValidationStatus
    validation_report: Dict[str, Any]
    teacher_action: DraftTeacherAction
    published_problem_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class QuestionGenerationJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    class_id: int
    assignment_id: Optional[int]
    status: QuestionGenerationStatus
    topic: str
    knowledge_points: List[str]
    request_payload: Dict[str, Any]
    retrieval_summary: Dict[str, Any]
    blueprint_json: Dict[str, Any]
    error_message: Optional[str]
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    created_at: datetime


class QuestionGenerationJobDetail(QuestionGenerationJobRead):
    drafts: List[QuestionDraftRead]
    validations: List[QuestionValidationRunRead]


class QuestionDraftRegenerateResponse(BaseModel):
    message: str
    draft: QuestionDraftRead


class QuestionGenerationPublishRequest(BaseModel):
    assignment_id: int
    accepted_draft_ids: List[int] = Field(default_factory=list)


class QuestionGenerationPublishResponse(BaseModel):
    created_problem_ids: List[int]
    message: str