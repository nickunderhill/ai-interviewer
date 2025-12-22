"""
Service layer for interview session business logic.
"""

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.user import User
from app.schemas.session import SessionCreate


async def create_session(
    db: AsyncSession, session_data: SessionCreate, current_user: User
) -> InterviewSession:
    """Create a new interview session."""

    # Fetch job posting with user validation
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.id == session_data.job_posting_id,
            JobPosting.user_id == current_user.id,
        )
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOB_POSTING_NOT_FOUND",
                "message": "Job posting not found or you don't have permission to access it",
            },
        )

    # Create session
    new_session = InterviewSession(
        user_id=current_user.id,
        job_posting_id=session_data.job_posting_id,
        status="active",
        current_question_number=0,
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session, ["job_posting"])

    return new_session
