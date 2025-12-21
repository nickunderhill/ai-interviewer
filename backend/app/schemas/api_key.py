"""
Schemas for API key management.
"""

from pydantic import BaseModel, Field


class ApiKeySetRequest(BaseModel):
    """Request schema for setting user's API key."""

    api_key: str = Field(min_length=1, description="OpenAI API key")


class ApiKeySetResponse(BaseModel):
    """Response schema after setting API key."""

    message: str = "API key configured successfully"
