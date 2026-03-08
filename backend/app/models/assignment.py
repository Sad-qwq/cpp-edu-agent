from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import JSON

class ProblemType(str, Enum):
    CHOICE = "choice"
    SHORT_ANSWER = "short_answer"
    CODING = "coding"

# --- Assignment Models ---

class AssignmentBase(SQLModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    classroom_id: int = Field(foreign_key="classroom.id")

class Assignment(AssignmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    problems: List["Problem"] = Relationship(back_populates="assignment", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    submissions: List["Submission"] = Relationship(back_populates="assignment", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentRead(AssignmentBase):
    id: int
    created_at: datetime
    # Extra fields for current user context (student side)
    my_submitted: Optional[bool] = None
    my_score: Optional[int] = None
    my_submission_id: Optional[int] = None

class AssignmentUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None

# --- Problem Models ---

class ProblemBase(SQLModel):
    type: ProblemType = Field(default=ProblemType.CHOICE)
    content: str  # Question text (Markdown)
    score: int = 10
    display_order: int = 0
    
    # Specific fields
    # For choice: ["A. Option 1", "B. Option 2"]
    options: List[str] = Field(default=[], sa_column=Column(JSON)) 
    correct_answer: Optional[str] = None
    code_template: Optional[str] = None
    # For coding: [{"input": "1 2", "output": "3"}, {"input": "0 0", "output": "0"}]
    test_cases: List[Dict[str, str]] = Field(default=[], sa_column=Column(JSON))

class Problem(ProblemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: int = Field(foreign_key="assignment.id")
    
    assignment: Optional[Assignment] = Relationship(back_populates="problems")

class ProblemCreate(ProblemBase):
    pass

class ProblemRead(ProblemBase):
    id: int
    assignment_id: int


class ProblemUpdate(SQLModel):
    type: Optional[ProblemType] = None
    content: Optional[str] = None
    score: Optional[int] = None
    display_order: Optional[int] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    code_template: Optional[str] = None
    test_cases: Optional[List[Dict[str, str]]] = None

# --- Submission Models ---

class SubmissionBase(SQLModel):
    assignment_id: int = Field(foreign_key="assignment.id")
    student_id: int = Field(foreign_key="user.id")

class Submission(SubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Stores answers in JSON format: 
    # Key: problem_id (str), Value: { "answer": "...", "file_url": "..." }
    answers: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    score: Optional[int] = None # Total score given by teacher
    feedback: Optional[str] = None # Teacher feedback

    assignment: Optional[Assignment] = Relationship(back_populates="submissions")

class SubmissionCreate(SubmissionBase):
    answers: Dict[str, Any]

class SubmissionGrade(SQLModel):
    score: int
    feedback: Optional[str] = None

class SubmissionRead(SubmissionBase):
    id: int
    submitted_at: datetime
    answers: Dict[str, Any]
    score: Optional[int]
    feedback: Optional[str]
    student_name: Optional[str] = None
