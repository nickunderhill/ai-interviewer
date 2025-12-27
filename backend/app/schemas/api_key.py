"""
Schemas for API key management.
"""

from pydantic import BaseModel, Field, field_validator

from app.utils.validators import ensure_not_blank


class ApiKeySetRequest(BaseModel):
    """Request schema for setting user's API key."""

    api_key: str = Field(
        min_length=1,
        max_length=256,
        description="OpenAI API key (must start with 'sk-')",
    )

    @field_validator("api_key", mode="before")
    @classmethod
    def normalize_api_key(cls, v: str):
        return ensure_not_blank(v)


class ApiKeySetResponse(BaseModel):
    """Response schema after setting API key."""

    message: str = "API key configured successfully"
