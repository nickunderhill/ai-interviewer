"""
Pydantic schemas for Job Posting API requests and responses.
"""

import datetime as dt
import uuid
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.validators import ensure_not_blank, normalize_optional_text


class JobPostingCreate(BaseModel):
    """Schema for creating a new job posting."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Job title",
    )
    company: str | None = Field(
        None,
        max_length=255,
        description="Company name",
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Job description",
    )
    experience_level: str | None = Field(
        None,
        max_length=50,
        description="Experience level (e.g., Junior, Mid-level, Senior)",
    )
    tech_stack: list[str] | None = Field(
        default_factory=list,
        description="Technologies required (e.g., ['Python', 'React'])",
    )
    language: Literal["en", "ua"] = Field(
        default="en",
        description="Language for AI-generated content",
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_required_text(cls, v: str):
        return ensure_not_blank(v)

    @field_validator("company", "experience_level", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, v: str | None):
        return normalize_optional_text(v)


class JobPostingUpdate(BaseModel):
    """Schema for updating an existing job posting."""

    title: str = Field(..., min_length=1, max_length=255)
    company: str | None = Field(None, max_length=255)
    description: str = Field(..., min_length=1, max_length=10000)
    experience_level: str | None = Field(None, max_length=50)
    tech_stack: list[str] | None = Field(default_factory=list)
    language: Literal["en", "ua"] = Field(
        default="en",
        description="Language for AI-generated content",
    )

    @field_validator("title", "description", mode="before")
    @classmethod
    def normalize_required_text(cls, v: str):
        return ensure_not_blank(v)

    @field_validator("company", "experience_level", mode="before")
    @classmethod
    def normalize_optional_text_fields(cls, v: str | None):
        return normalize_optional_text(v)

    @field_validator("tech_stack")
    @classmethod
    def validate_tech_stack_elements(cls, v: list[str] | None):
        """Validate tech_stack elements are non-empty and reasonable length."""
        if v is not None:
            for tech in v:
                if not tech or not tech.strip():
                    raise ValueError("Tech stack items cannot be empty")
                if len(tech) > 100:
                    msg = "Tech stack items cannot exceed 100 characters"
                    raise ValueError(msg)
        return v or []


class JobPostingResponse(BaseModel):
    """Schema for full job posting response (with description)."""

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    company: str | None
    description: str
    experience_level: str | None
    tech_stack: list[str] | None
    language: str
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class JobPostingListItem(BaseModel):
    """Schema for job posting list items.

    Excludes description field for performance optimization.
    """

    id: uuid.UUID
    title: str
    company: str | None
    experience_level: str | None
    tech_stack: list[str] | None
    created_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)
