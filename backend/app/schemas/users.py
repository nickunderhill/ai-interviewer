"""
User profile schemas.
Schemas for user profile viewing and management.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserProfileResponse(BaseModel):
    """User profile response (never includes password)."""

    id: uuid.UUID
    email: EmailStr
    created_at: datetime
