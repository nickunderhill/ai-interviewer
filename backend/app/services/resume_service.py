"""
Resume service - business logic for resume operations.
"""

import datetime as dt
import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume


class ResumeConflictException(HTTPException):
    """Exception raised when user tries to create duplicate resume."""

    def __init__(self, detail: str = "User already has a resume"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class ResumeNotFoundException(HTTPException):
    """Exception raised when resume is not found."""

    def __init__(self, detail: str = "Resume not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


async def create_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
    content: str,
) -> Resume:
    """
    Create a new resume for a user.

    Args:
        db: Database session
        user_id: ID of the user creating the resume
        content: Resume content in plain text

    Returns:
        Created Resume object

    Raises:
        ResumeConflictException: If user already has a resume
    """
    # Check if user already has a resume
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    existing_resume = result.scalar_one_or_none()

    if existing_resume:
        raise ResumeConflictException()

    # Create new resume
    resume = Resume(
        user_id=user_id,
        content=content,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)

    return resume


async def get_user_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Resume | None:
    """
    Retrieve a user's resume.

    Args:
        db: Database session
        user_id: ID of the user

    Returns:
        Resume object if found, None otherwise
    """
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    return result.scalar_one_or_none()


async def update_user_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
    content: str,
) -> Resume:
    """
    Update a user's resume content.

    Args:
        db: Database session
        user_id: ID of the user
        content: New resume content

    Returns:
        Updated Resume object

    Raises:
        ResumeNotFoundException: If user has no resume
    """
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    resume = result.scalar_one_or_none()

    if not resume:
        raise ResumeNotFoundException()

    # Update content and timestamp
    resume.content = content
    resume.updated_at = dt.datetime.now(dt.UTC)
    await db.commit()
    await db.refresh(resume)

    return resume


async def delete_user_resume(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    """
    Delete a user's resume.

    Args:
        db: Database session
        user_id: ID of the user

    Raises:
        ResumeNotFoundException: If user has no resume
    """
    result = await db.execute(select(Resume).where(Resume.user_id == user_id))
    resume = result.scalar_one_or_none()

    if not resume:
        raise ResumeNotFoundException()

    await db.delete(resume)
    await db.commit()
