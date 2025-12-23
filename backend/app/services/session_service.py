"""
Service layer for interview session business logic.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.session_message import SessionMessage
from app.models.user import User
from app.schemas.session import SessionCreate, AnswerCreate


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
                "message": (
                    "Job posting not found or you don't have " "permission to access it"
                ),
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


async def get_sessions_by_user(
    db: AsyncSession, current_user: User, status_filter: Optional[str] = None
) -> List[InterviewSession]:
    """Get all sessions for a user, optionally filtered by status."""

    # Validate status if provided
    valid_statuses = ["active", "paused", "completed"]
    if status_filter and status_filter not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_FILTER",
                "message": (
                    "Invalid status filter. Must be one of: "
                    "active, paused, completed"
                ),
            },
        )

    # Build query with eager loading
    query = (
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .options(selectinload(InterviewSession.job_posting))
    )

    # Apply status filter if provided
    if status_filter:
        query = query.where(InterviewSession.status == status_filter)

    # Order by newest first
    query = query.order_by(InterviewSession.created_at.desc())

    result = await db.execute(query)
    sessions = result.scalars().all()

    return list(sessions)


async def get_session_by_id(
    db: AsyncSession, session_id: UUID, current_user: User
) -> InterviewSession:
    """Get a session by ID with full details."""

    # Query with eager loading for job_posting and user.resume
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
        .options(
            selectinload(InterviewSession.job_posting),
            selectinload(InterviewSession.user).selectinload(User.resume),
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": (
                    "Session not found or you don't have " "permission to access it"
                ),
            },
        )

    return session


async def submit_answer(
    db: AsyncSession, session_id: UUID, answer_data: AnswerCreate, current_user: User
) -> SessionMessage:
    """
    Submit an answer to an interview session.

    Args:
        db: Database session
        session_id: UUID of the session
        answer_data: Answer content
        current_user: Authenticated user

    Returns:
        Created SessionMessage

    Raises:
        HTTPException: If session not found, unauthorized, or not active
    """
    # Load and validate session
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found or you don't have permission to access it",
            },
        )

    # Validate session is active
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_NOT_ACTIVE",
                "message": f"Cannot submit answers to {session.status} session. Only active sessions accept answers.",
            },
        )

    # Create answer message
    message = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content=answer_data.answer_text,
        question_type=None,  # Answers don't have question types
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message
