from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, SQLModel


class DiscussionQuestionBase(SQLModel):
    title: str
    content: str = Field(sa_column=Column(Text))
    upvote_count: int = 0
    accepted_answer_id: Optional[int] = None
    is_locked: bool = False


class DiscussionQuestion(DiscussionQuestionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    class_id: int = Field(foreign_key="classroom.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class DiscussionAnswerBase(SQLModel):
    content: str = Field(sa_column=Column(Text))
    upvote_count: int = 0
    is_accepted: bool = False


class DiscussionAnswer(DiscussionAnswerBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="discussionquestion.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QuestionVote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="discussionquestion.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnswerVote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    answer_id: int = Field(foreign_key="discussionanswer.id")
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
