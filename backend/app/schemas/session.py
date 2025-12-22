"""
Pydantic schemas for interview session API.
"""

import datetime as dt
from typing import Optional
from pydantic import BaseModel, ConfigDict, UUID4


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
