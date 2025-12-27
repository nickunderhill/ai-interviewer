"""
Pydantic schemas for Resume API requests and responses.
"""

import datetime as dt
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ResumeCreate(BaseModel):
    """Schema for creating a new resume."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Resume content in plain text format",
    )


class ResumeUpdate(BaseModel):
    """Schema for updating an existing resume."""

    content: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Updated resume content in plain text format",
    )


class ResumeResponse(BaseModel):
    """Schema for resume API responses."""

    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
