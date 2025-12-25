"""
Tests for InterviewSession model.
"""

import datetime as dt
import uuid as uuid_module

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_interview_session_creation_with_all_relationships(db_session):
    """Test InterviewSession creation with user and job posting relationships."""
    from app.models.interview_session import InterviewSession
    from app.models.job_posting import JobPosting
    from app.models.user import User

    # Create user
    user = User(email="session_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create job posting
    job_posting = JobPosting(
        user_id=user.id,
        title="Software Engineer",
        company="Test Corp",
        description="Test description",
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    # Create interview session
    session = InterviewSession(
        user_id=user.id,
        job_posting_id=job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.id is not None
    assert isinstance(session.id, uuid_module.UUID)
    assert session.user_id == user.id
    assert session.job_posting_id == job_posting.id
    assert session.status == "active"
    assert session.current_question_number == 0


@pytest.mark.asyncio
async def test_interview_session_status_field_accepts_valid_values(db_session):
    """Test that status field accepts valid string values."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="status_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    for status in ["active", "paused", "completed"]:
        session = InterviewSession(
            user_id=user.id,
            job_posting_id=None,
            status=status,
            current_question_number=0,
        )
        db_session.add(session)
        await db_session.commit()
        await db_session.refresh(session)

        assert session.status == status


@pytest.mark.asyncio
async def test_interview_session_current_question_number_defaults_to_zero(db_session):
    """Test that current_question_number defaults to 0."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="default_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.current_question_number == 0


@pytest.mark.asyncio
async def test_interview_session_cascade_behavior_on_user_deletion(db_session):
    """Test that deleting user cascades to delete sessions."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="cascade_user@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    session_id = session.id

    # Delete user
    await db_session.delete(user)
    await db_session.commit()

    # Verify session was also deleted
    result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    deleted_session = result.scalar_one_or_none()
    assert deleted_session is None


@pytest.mark.asyncio
async def test_interview_session_set_null_on_job_posting_deletion(db_session):
    """Test that deleting job posting sets job_posting_id to NULL."""
    from app.models.interview_session import InterviewSession
    from app.models.job_posting import JobPosting
    from app.models.user import User

    user = User(email="set_null_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    job_posting = JobPosting(
        user_id=user.id,
        title="Test Job",
        description="Test description",
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    session_id = session.id

    # Delete job posting
    await db_session.delete(job_posting)
    await db_session.commit()

    # Verify session still exists but job_posting_id is NULL
    result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    updated_session = result.scalar_one_or_none()
    assert updated_session is not None
    assert updated_session.job_posting_id is None


@pytest.mark.asyncio
async def test_interview_session_timestamps_are_utc_aware(db_session):
    """Test that timestamps are UTC-aware."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="timestamp_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.created_at is not None
    assert session.created_at.tzinfo is not None
    assert session.created_at.utcoffset() == dt.timedelta(0)

    assert session.updated_at is not None
    assert session.updated_at.tzinfo is not None
    assert session.updated_at.utcoffset() == dt.timedelta(0)


@pytest.mark.asyncio
async def test_interview_session_user_id_required(db_session):
    """Test that user_id is required (NOT NULL)."""
    from app.models.interview_session import InterviewSession

    session = InterviewSession(
        user_id=None,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


@pytest.mark.asyncio
async def test_interview_session_job_posting_id_nullable(db_session):
    """Test that job_posting_id can be NULL."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="nullable_job@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    assert session.job_posting_id is None


@pytest.mark.asyncio
async def test_interview_session_relationship_with_user(db_session):
    """Test that session has working relationship with user."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="relationship_test@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Test forward relationship
    assert session.user is not None
    assert session.user.email == "relationship_test@example.com"

    # Test back-populate relationship
    await db_session.refresh(user)
    assert len(user.interview_sessions) == 1
    assert user.interview_sessions[0].id == session.id
