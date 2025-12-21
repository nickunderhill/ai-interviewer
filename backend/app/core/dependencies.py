"""
Authentication dependencies for FastAPI routes.
Provides dependency injection for current user authentication.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_token_payload
from app.core.database import get_db
from app.models.user import User


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_payload: dict[str, Any] = Depends(get_token_payload),
) -> User:
    """
    Dependency that validates JWT token and returns the current authenticated user.

    Validates the token and loads the user from the database.
    Returns 401 Unauthorized if:
    - Token is missing
    - Token is invalid
    - Token is expired
    - User not found in database

    Args:
        db: Database session
        token_payload: Decoded JWT token payload

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: 401 if authentication fails
    """
    user_id_str = token_payload.get("user_id")

    if not user_id_str:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Token missing user_id.",
            },
        )

    try:
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError) as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid user_id format in token.",
            },
        ) from exc

    # Load user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "User no longer exists.",
            },
        )

    return user
