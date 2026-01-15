"""
Job Posting API endpoints.

Provides CRUD operations for job postings:
- POST / - Create new job posting
- GET / - List all user's job postings (summary without description)
- GET /{id} - Get specific job posting with full details
- PUT /{id} - Update existing job posting
- DELETE /{id} - Delete job posting

All endpoints require authentication via JWT token.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.job_posting import (
    JobPostingCreate,
    JobPostingListItem,
    JobPostingResponse,
    JobPostingUpdate,
)
from app.services import job_posting_service

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=JobPostingResponse,
    summary="Create Job Posting",
    description="Create a new job posting for interview practice",
)
async def create_job_posting(
    job_posting_data: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobPostingResponse:
    """
    Create a new job posting.

    - **title**: Job title (required, 1-255 characters)
    - **description**: Job description (required, 1-10,000 characters)
    - **company**: Company name (optional, max 255 characters)
    - **experience_level**: Experience level (optional, max 50 characters)
    - **tech_stack**: Array of technologies (optional)

    Returns 201 Created with job posting data.
    Returns 401 Unauthorized if not authenticated.
    Returns 422 Validation Error if data is invalid.
    """
    job_posting = await job_posting_service.create_job_posting(
        db=db,
        user_id=current_user.id,
        title=job_posting_data.title,
        description=job_posting_data.description,
        company=job_posting_data.company,
        experience_level=job_posting_data.experience_level,
        tech_stack=job_posting_data.tech_stack,
        language=job_posting_data.language,
    )
    return job_posting


@router.get(
    "/",
    response_model=list[JobPostingListItem],
    summary="List Job Postings",
    description="Get list of all job postings for authenticated user",
)
async def list_job_postings(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[JobPostingListItem]:
    """
    Get list of user's job postings (ordered by created_at DESC).

    Returns summary data without description field for performance.
    Returns empty array if user has no job postings.
    Supports pagination via limit/offset parameters.
    Returns 401 Unauthorized if not authenticated.
    """
    job_postings = await job_posting_service.get_user_job_postings(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return job_postings


@router.get(
    "/{job_posting_id}",
    response_model=JobPostingResponse,
    summary="Get Job Posting",
    description="Get specific job posting with full details",
)
async def get_job_posting(
    job_posting_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobPostingResponse:
    """
    Get specific job posting by ID.

    Returns full job posting data including description.
    Returns 404 Not Found if job posting doesn't exist or
    belongs to another user.
    Returns 401 Unauthorized if not authenticated.
    """
    job_posting = await job_posting_service.get_job_posting_by_id(
        db=db,
        job_posting_id=job_posting_id,
        user_id=current_user.id,
    )
    return job_posting


@router.put(
    "/{job_posting_id}",
    response_model=JobPostingResponse,
    summary="Update Job Posting",
    description="Update existing job posting",
)
async def update_job_posting(
    job_posting_id: UUID,
    job_posting_data: JobPostingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobPostingResponse:
    """
    Update existing job posting (full replacement).

    All fields must be provided (PUT semantics).
    Returns 200 OK with updated job posting data.
    Returns 404 Not Found if job posting doesn't exist or
    belongs to another user.
    Returns 401 Unauthorized if not authenticated.
    Returns 422 Validation Error if data is invalid.
    """
    job_posting = await job_posting_service.update_job_posting(
        db=db,
        job_posting_id=job_posting_id,
        user_id=current_user.id,
        title=job_posting_data.title,
        description=job_posting_data.description,
        company=job_posting_data.company,
        experience_level=job_posting_data.experience_level,
        tech_stack=job_posting_data.tech_stack,
        language=job_posting_data.language,
    )
    return job_posting


@router.delete(
    "/{job_posting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Job Posting",
    description="Delete job posting permanently",
)
async def delete_job_posting(
    job_posting_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """
    Delete job posting permanently.

    Returns 204 No Content on success.
    Returns 404 Not Found if job posting doesn't exist or
    belongs to another user.
    Returns 401 Unauthorized if not authenticated.
    """
    await job_posting_service.delete_job_posting(
        db=db,
        job_posting_id=job_posting_id,
        user_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
