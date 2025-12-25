"""
Pydantic schemas for interview session API.
"""

import datetime as dt
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, UUID4


class SessionCreate(BaseModel):
    """Request schema for creating an interview session."""

    job_posting_id: UUID4


class JobPostingBasic(BaseModel):
    """Nested job posting info for session response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    company: Optional[str] = None


class SessionResponse(BaseModel):
    """Response schema for interview session."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    job_posting_id: Optional[UUID4] = None
    status: str
    current_question_number: int
    created_at: dt.datetime
    updated_at: dt.datetime
    job_posting: Optional[JobPostingBasic] = None


class JobPostingDetail(BaseModel):
    """Complete job posting details for session detail response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    company: Optional[str] = None
    description: str
    experience_level: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)


class ResumeDetail(BaseModel):
    """Resume details for session detail response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    content: str


class MessageResponse(BaseModel):
    """Response schema for SessionMessage."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    session_id: UUID4
    message_type: str
    content: str
    question_type: Optional[str] = None
    created_at: dt.datetime


class SessionDetailResponse(BaseModel):
    """Detailed session response including full job posting and resume."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    job_posting_id: Optional[UUID4] = None
    status: str
    current_question_number: int
    created_at: dt.datetime
    updated_at: dt.datetime
    job_posting: Optional[JobPostingDetail] = None
    resume: Optional[ResumeDetail] = None
    messages: List[MessageResponse] = Field(default_factory=list)


class SessionWithFeedbackScore(BaseModel):
    """Session with feedback score for comparison views."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID4
    created_at: dt.datetime
    job_posting: JobPostingBasic
    overall_score: float


class AnswerCreate(BaseModel):
    """Request schema for submitting an answer."""

    answer_text: str = Field(..., min_length=1, description="User's answer text")
