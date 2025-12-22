"""
Resume API endpoints.

Provides CRUD operations for user resumes:
- POST / - Create new resume (one per user)
- GET /me - Retrieve authenticated user's resume
- PUT /me - Update existing resume content
- DELETE /me - Delete resume

All endpoints require authentication via JWT token.

TODO: Add rate limiting middleware to prevent abuse (Issue #8 from code review).
      Recommended: fastapi-limiter or slowapi with Redis backend.
      See stories 3.2-3.5 Security Considerations.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.services import resume_service

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResumeResponse,
    summary="Create Resume",
    description="Upload or paste resume content in plain text format",
)
async def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """
    Create a new resume for the authenticated user.

    - **content**: Resume content in plain text (1-50,000 characters)

    Returns 201 Created with resume data.
    Returns 409 Conflict if user already has a resume.
    Returns 401 Unauthorized if not authenticated.
    Returns 422 Validation Error if content is invalid.
    """
    resume = await resume_service.create_resume(
        db=db,
        user_id=current_user.id,
        content=resume_data.content,
    )
    return resume


@router.get(
    "/me",
    response_model=ResumeResponse,
    summary="Get My Resume",
    description="Retrieve the authenticated user's resume",
)
async def get_my_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """
    Get the current user's resume.

    Returns 200 OK with resume data if found.
    Returns 404 Not Found if user has no resume.
    Returns 401 Unauthorized if not authenticated.
    """
    resume = await resume_service.get_user_resume(db=db, user_id=current_user.id)

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    return resume


@router.put(
    "/me",
    response_model=ResumeResponse,
    summary="Update My Resume",
    description="Update the authenticated user's resume content",
)
async def update_my_resume(
    resume_data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeResponse:
    """
    Update the current user's resume.

    - **content**: New resume content (1-50,000 characters)

    Returns 200 OK with updated resume data.
    Returns 404 Not Found if user has no resume.
    Returns 401 Unauthorized if not authenticated.
    Returns 422 Validation Error if content is invalid.
    """
    resume = await resume_service.update_user_resume(
        db=db,
        user_id=current_user.id,
        content=resume_data.content,
    )
    return resume


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete My Resume",
    description="Delete the authenticated user's resume",
)
async def delete_my_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete the current user's resume.

    Returns 204 No Content on success.
    Returns 404 Not Found if user has no resume.
    Returns 401 Unauthorized if not authenticated.
    """
    await resume_service.delete_user_resume(db=db, user_id=current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
