"""
User endpoints.
API endpoints for user profile management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.users import UserProfileResponse
from app.schemas.api_key import ApiKeySetRequest, ApiKeySetResponse
from app.services.encryption_service import encrypt_api_key

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfileResponse:
    """
    Get the authenticated user's profile.

    Returns profile information for the currently authenticated user.
    Never includes password or other sensitive data.

    Returns:
        UserProfileResponse: User profile with id, email, and created_at

    Raises:
        HTTPException: 401 if not authenticated
    """
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        created_at=current_user.created_at,
    )


@router.post("/me/api-key", response_model=ApiKeySetResponse)
async def set_api_key(
    payload: ApiKeySetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiKeySetResponse:
    """
    Configure the authenticated user's OpenAI API key.

    Encrypts the API key before storing it in the database.
    Never returns the API key in the response.

    Args:
        payload: Request containing the API key
        current_user: Authenticated user
        db: Database session

    Returns:
        ApiKeySetResponse: Success message

    Raises:
        HTTPException: 401 if not authenticated
    """
    # Encrypt the API key before storing
    encrypted_key = encrypt_api_key(payload.api_key)

    # Update user's encrypted API key
    current_user.encrypted_api_key = encrypted_key
    await db.commit()

    return ApiKeySetResponse()


@router.put("/me/api-key", response_model=ApiKeySetResponse)
async def update_api_key(
    payload: ApiKeySetRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ApiKeySetResponse:
    """
    Update the authenticated user's OpenAI API key.

    Encrypts the new API key before storing it in the database.
    Overwrites any existing API key.
    Never returns the API key in the response.

    Args:
        payload: Request containing the new API key
        current_user: Authenticated user
        db: Database session

    Returns:
        ApiKeySetResponse: Success message

    Raises:
        HTTPException: 401 if not authenticated
    """
    # Encrypt the new API key before storing
    encrypted_key = encrypt_api_key(payload.api_key)

    # Update user's encrypted API key (overwrites existing)
    current_user.encrypted_api_key = encrypted_key
    await db.commit()

    return ApiKeySetResponse()
