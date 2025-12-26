"""
Pydantic schemas for interview session API.
"""

import datetime as dt

from pydantic import UUID4, BaseModel, ConfigDict, Field


class SessionCreate(BaseModel):
    """Request schema for creating an interview session."""

    job_posting_id: UUID4


class JobPostingBasic(BaseModel):
    """Nested job posting info for session response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    company: str | None = None


class SessionResponse(BaseModel):
    """Response schema for interview session."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    job_posting_id: UUID4 | None = None
    status: str
    current_question_number: int
    retake_number: int = Field(
        default=1,
        description="Attempt number (1 = first attempt, 2 = first retake, etc.)",
    )
    original_session_id: UUID4 | None = Field(
        default=None,
        description="ID of the original session for this job posting (null for first attempts)",
    )
    created_at: dt.datetime
    updated_at: dt.datetime
    job_posting: JobPostingBasic | None = None


class JobPostingDetail(BaseModel):
    """Complete job posting details for session detail response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    company: str | None = None
    description: str
    experience_level: str | None = None
    tech_stack: list[str] = Field(default_factory=list)


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
    question_type: str | None = None
    created_at: dt.datetime


class SessionDetailResponse(BaseModel):
    """Detailed session response including full job posting and resume."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    job_posting_id: UUID4 | None = None
    status: str
    current_question_number: int
    retake_number: int = Field(
        default=1,
        description="Attempt number (1 = first attempt, 2 = first retake, etc.)",
    )
    original_session_id: UUID4 | None = Field(
        default=None,
        description="ID of the original session for this job posting (null for first attempts)",
    )
    created_at: dt.datetime
    updated_at: dt.datetime
    job_posting: JobPostingDetail | None = None
    resume: ResumeDetail | None = None
    messages: list[MessageResponse] = Field(default_factory=list)


class SessionWithFeedbackScore(BaseModel):
    """Session with feedback score for comparison views."""

    model_config = ConfigDict(from_attributes=True)

    session_id: UUID4
    created_at: dt.datetime
    job_posting: JobPostingBasic
    overall_score: float
    retake_number: int = Field(
        default=1,
        description="Attempt number (1 = first attempt, 2 = first retake, etc.)",
    )
    original_session_id: UUID4 | None = Field(
        default=None,
        description="ID of the original session for this job posting (null for first attempts)",
    )


class AnswerCreate(BaseModel):
    """Request schema for submitting an answer."""

    answer_text: str = Field(..., min_length=1, description="User's answer text")
