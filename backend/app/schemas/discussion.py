from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from app.models.user import UserRole


class UserBrief(BaseModel):
    id: int
    username: Optional[str] = None
    role: UserRole
    avatar_url: Optional[str] = None


class DiscussionQuestionCreate(BaseModel):
    title: str
    content: str


class DiscussionQuestionRead(BaseModel):
    id: int
    class_id: int
    user_id: int
    title: str
    content: str
    upvote_count: int
    accepted_answer_id: Optional[int] = None
    is_locked: bool
    created_at: datetime
    updated_at: datetime
    author: Optional[UserBrief] = None
    answer_count: int = 0


class DiscussionAnswerCreate(BaseModel):
    content: str


class DiscussionAnswerRead(BaseModel):
    id: int
    question_id: int
    user_id: int
    content: str
    upvote_count: int
    is_accepted: bool
    created_at: datetime
    updated_at: datetime
    author: Optional[UserBrief] = None


class DiscussionQuestionDetail(DiscussionQuestionRead):
    answers: List[DiscussionAnswerRead] = []


class DiscussionQuestionListResponse(BaseModel):
    items: List[DiscussionQuestionRead]
    total: int


class VoteResponse(BaseModel):
    target_id: int
    upvote_count: int
    user_voted: bool
