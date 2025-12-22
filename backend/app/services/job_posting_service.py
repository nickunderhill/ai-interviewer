"""
Job Posting service - business logic for job posting operations.
"""

import datetime as dt
import uuid
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job_posting import JobPosting


class JobPostingNotFoundException(HTTPException):
    """Exception raised when job posting is not found."""

    def __init__(self, detail: str = "Job posting not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


async def create_job_posting(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: str,
    description: str,
    company: Optional[str] = None,
    experience_level: Optional[str] = None,
    tech_stack: Optional[List[str]] = None,
) -> JobPosting:
    """
    Create a new job posting for a user.

    Args:
        db: Database session
        user_id: ID of the user creating the job posting
        title: Job title
        description: Job description
        company: Company name (optional)
        experience_level: Experience level (optional)
        tech_stack: List of technologies (optional)

    Returns:
        Created JobPosting object
    """
    job_posting = JobPosting(
        user_id=user_id,
        title=title,
        company=company,
        description=description,
        experience_level=experience_level,
        tech_stack=tech_stack,
    )
    db.add(job_posting)
    await db.commit()
    await db.refresh(job_posting)

    return job_posting


async def get_user_job_postings(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> List[JobPosting]:
    """
    Retrieve job postings for a user (ordered by created_at DESC).

    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)

    Returns:
        List of JobPosting objects (empty list if none)
    """
    result = await db.execute(
        select(JobPosting)
        .where(JobPosting.user_id == user_id)
        .order_by(JobPosting.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_job_posting_by_id(
    db: AsyncSession,
    job_posting_id: uuid.UUID,
    user_id: uuid.UUID,
) -> JobPosting:
    """
    Retrieve a specific job posting by ID (with ownership check).

    Args:
        db: Database session
        job_posting_id: ID of the job posting
        user_id: ID of the user (for ownership verification)

    Returns:
        JobPosting object

    Raises:
        JobPostingNotFoundException: If not found or not owned by user
    """
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.id == job_posting_id,
            JobPosting.user_id == user_id,
        )
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        raise JobPostingNotFoundException()

    return job_posting


async def update_job_posting(
    db: AsyncSession,
    job_posting_id: uuid.UUID,
    user_id: uuid.UUID,
    title: str,
    description: str,
    company: Optional[str] = None,
    experience_level: Optional[str] = None,
    tech_stack: Optional[List[str]] = None,
) -> JobPosting:
    """
    Update a job posting.

    Args:
        db: Database session
        job_posting_id: ID of the job posting
        user_id: ID of the user (for ownership verification)
        title: Updated job title
        description: Updated job description
        company: Updated company name (optional)
        experience_level: Updated experience level (optional)
        tech_stack: Updated tech stack (optional)

    Returns:
        Updated JobPosting object

    Raises:
        JobPostingNotFoundException: If job posting not found or not owned by user
    """
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.id == job_posting_id,
            JobPosting.user_id == user_id,
        )
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        raise JobPostingNotFoundException()

    # Update fields and timestamp
    job_posting.title = title
    job_posting.company = company
    job_posting.description = description
    job_posting.experience_level = experience_level
    job_posting.tech_stack = tech_stack
    job_posting.updated_at = dt.datetime.now(dt.timezone.utc)

    await db.commit()
    await db.refresh(job_posting)

    return job_posting


async def delete_job_posting(
    db: AsyncSession,
    job_posting_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """
    Delete a job posting.

    Args:
        db: Database session
        job_posting_id: ID of the job posting
        user_id: ID of the user (for ownership verification)

    Raises:
        JobPostingNotFoundException: If not found or not owned by user
    """
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.id == job_posting_id,
            JobPosting.user_id == user_id,
        )
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        raise JobPostingNotFoundException()

    await db.delete(job_posting)
    await db.commit()
