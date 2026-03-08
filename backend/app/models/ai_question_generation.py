from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class KnowledgeSourceType(str, Enum):
    ADMIN_MATERIAL = "admin_material"
    CLASS_MATERIAL = "class_material"
    HISTORY_PROBLEM = "history_problem"
    MANUAL_ENTRY = "manual_entry"


class KnowledgeParseStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestionGenerationStatus(str, Enum):
    PENDING = "pending"
    RETRIEVING = "retrieving"
    BLUEPRINTING = "blueprinting"
    GENERATING = "generating"
    VALIDATING = "validating"
    REVIEWING = "reviewing"
    PUBLISHED = "published"
    FAILED = "failed"


class DraftValidationStatus(str, Enum):
    PENDING = "pending"
    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


class DraftTeacherAction(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EDITED = "edited"
    REJECTED = "rejected"
    REGENERATED = "regenerated"


class ValidationType(str, Enum):
    SCHEMA = "schema"
    SEMANTIC = "semantic"
    DUPLICATE = "duplicate"
    CODING_EXECUTION = "coding_execution"


class KnowledgeDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_type: KnowledgeSourceType = Field(default=KnowledgeSourceType.CLASS_MATERIAL)
    source_id: Optional[int] = None
    class_id: Optional[int] = Field(default=None, foreign_key="classroom.id")
    teacher_id: Optional[int] = Field(default=None, foreign_key="user.id")
    title: str
    file_path: Optional[str] = None
    mime_type: Optional[str] = None
    parse_status: KnowledgeParseStatus = Field(default=KnowledgeParseStatus.PENDING)
    parse_error: Optional[str] = None
    metadata_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeChunk(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: int = Field(foreign_key="knowledgedocument.id", index=True)
    chunk_index: int = 0
    content: str = Field(sa_column=Column(Text, nullable=False))
    content_type: str = "theory"
    token_count: int = 0
    knowledge_tags: List[str] = Field(default=[], sa_column=Column(JSON))
    metadata_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    embedding: List[float] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionGenerationJob(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="user.id", index=True)
    class_id: int = Field(foreign_key="classroom.id", index=True)
    assignment_id: Optional[int] = Field(default=None, foreign_key="assignment.id")
    status: QuestionGenerationStatus = Field(default=QuestionGenerationStatus.PENDING)
    topic: str
    knowledge_points: List[str] = Field(default=[], sa_column=Column(JSON))
    request_payload: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    retrieval_summary: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    blueprint_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionDraft(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="questiongenerationjob.id", index=True)
    draft_index: int = 0
    type: str
    content: str = Field(sa_column=Column(Text, nullable=False))
    options: List[str] = Field(default=[], sa_column=Column(JSON))
    correct_answer: Optional[str] = None
    code_template: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    test_cases: List[Dict[str, str]] = Field(default=[], sa_column=Column(JSON))
    reference_solution: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    explanation: Optional[str] = Field(default=None, sa_column=Column(Text, nullable=True))
    target_knowledge_points: List[str] = Field(default=[], sa_column=Column(JSON))
    difficulty: Optional[str] = None
    estimated_score: Optional[int] = None
    source_chunk_ids: List[int] = Field(default=[], sa_column=Column(JSON))
    validation_status: DraftValidationStatus = Field(default=DraftValidationStatus.PENDING)
    validation_report: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    teacher_action: DraftTeacherAction = Field(default=DraftTeacherAction.PENDING)
    published_problem_id: Optional[int] = Field(default=None, foreign_key="problem.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionValidationRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    draft_id: int = Field(foreign_key="questiondraft.id", index=True)
    validation_type: ValidationType
    status: DraftValidationStatus = Field(default=DraftValidationStatus.PENDING)
    report_json: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)