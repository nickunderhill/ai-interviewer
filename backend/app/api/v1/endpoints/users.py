"""
User endpoints.
API endpoints for user profile management.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.api_key import ApiKeySetRequest, ApiKeySetResponse
from app.schemas.users import UserProfileResponse
from app.services.encryption_service import encrypt_api_key
from app.utils.validators import validate_openai_api_key_format

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
        HTTPException: 400 if API key format is invalid
    """
    # Validate API key format
    try:
        validate_openai_api_key_format(payload.api_key)
    except ValueError as e:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_API_KEY_FORMAT", "message": str(e)},
        ) from e

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
        HTTPException: 400 if API key format is invalid
    """
    # Validate API key format
    try:
        validate_openai_api_key_format(payload.api_key)
    except ValueError as e:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_API_KEY_FORMAT", "message": str(e)},
        ) from e

    # Encrypt the new API key before storing
    encrypted_key = encrypt_api_key(payload.api_key)

    # Update user's encrypted API key (overwrites existing)
    current_user.encrypted_api_key = encrypted_key
    await db.commit()

    return ApiKeySetResponse()


@router.post("/me/api-key/validate")
async def validate_api_key(
    payload: ApiKeySetRequest,
    current_user: User = Depends(get_current_user),
) -> dict:
    """
    Validate an OpenAI API key without saving it.

    Tests the API key by making a simple OpenAI API call.
    Useful for pre-validation before saving the key.

    Args:
        payload: Request containing the API key to validate
        current_user: Authenticated user

    Returns:
        dict: Validation result with 'valid' boolean and optional 'message'

    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 400 if API key format is invalid
    """
    # Validate API key format first
    try:
        validate_openai_api_key_format(payload.api_key)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "INVALID_API_KEY_FORMAT", "message": str(e)},
        ) from e

    # Test the API key with OpenAI
    try:
        client = AsyncOpenAI(api_key=payload.api_key)
        # Make a minimal API call to validate the key
        await client.models.list()
        return {"valid": True, "message": "API key is valid and working"}
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Incorrect API key" in error_msg:
            return {
                "valid": False,
                "message": "Invalid API key. Please check your OpenAI API key.",
            }
        elif "429" in error_msg:
            return {
                "valid": False,
                "message": "Rate limit exceeded. Please try again later.",
            }
        else:
            return {
                "valid": False,
                "message": f"Could not validate API key: {error_msg}",
            }
