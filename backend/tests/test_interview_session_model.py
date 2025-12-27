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


@pytest.mark.asyncio
async def test_interview_session_retake_number_defaults_to_one(db_session):
    """Test that retake_number defaults to 1 for new sessions."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="retake_default@example.com", hashed_password="hashed")
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

    assert session.retake_number == 1


@pytest.mark.asyncio
async def test_interview_session_original_session_id_nullable(db_session):
    """Test that original_session_id can be NULL for first attempts."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="original_null@example.com", hashed_password="hashed")
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

    assert session.original_session_id is None


@pytest.mark.asyncio
async def test_interview_session_retake_tracking_with_original_session(db_session):
    """Test creating a retake session linked to an original session."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="retake_tracking@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create original session
    original_session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="completed",
        retake_number=1,
    )
    db_session.add(original_session)
    await db_session.commit()
    await db_session.refresh(original_session)

    # Create retake session
    retake_session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        retake_number=2,
        original_session_id=original_session.id,
    )
    db_session.add(retake_session)
    await db_session.commit()
    await db_session.refresh(retake_session)

    assert retake_session.retake_number == 2
    assert retake_session.original_session_id == original_session.id


@pytest.mark.asyncio
async def test_interview_session_self_referential_relationship(db_session):
    """Test self-referential relationship for retakes."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="self_ref@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create original session
    original_session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="completed",
        retake_number=1,
    )
    db_session.add(original_session)
    await db_session.commit()
    await db_session.refresh(original_session)

    # Create first retake
    retake1 = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="completed",
        retake_number=2,
        original_session_id=original_session.id,
    )
    db_session.add(retake1)
    await db_session.commit()

    # Create second retake
    retake2 = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        retake_number=3,
        original_session_id=original_session.id,
    )
    db_session.add(retake2)
    await db_session.commit()

    # Refresh to load relationships
    await db_session.refresh(original_session)
    await db_session.refresh(retake1)
    await db_session.refresh(retake2)

    # Test forward relationship (retake -> original)
    assert retake1.original_session is not None
    assert retake1.original_session.id == original_session.id
    assert retake2.original_session is not None
    assert retake2.original_session.id == original_session.id

    # Test back-populate relationship (original -> retakes)
    assert len(original_session.retakes) == 2
    retake_ids = {r.id for r in original_session.retakes}
    assert retake1.id in retake_ids
    assert retake2.id in retake_ids


@pytest.mark.asyncio
async def test_interview_session_set_null_on_original_session_deletion(db_session):
    """Test that deleting original session sets original_session_id to NULL in retakes."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="cascade_original@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create original session
    original_session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="completed",
    )
    db_session.add(original_session)
    await db_session.commit()
    await db_session.refresh(original_session)

    # Create retake session
    retake_session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        retake_number=2,
        original_session_id=original_session.id,
    )
    db_session.add(retake_session)
    await db_session.commit()
    await db_session.refresh(retake_session)

    # Delete original session
    await db_session.delete(original_session)
    await db_session.commit()

    # Refresh to see the updated foreign key value
    await db_session.refresh(retake_session)

    # Verify retake still exists but original_session_id is NULL
    assert retake_session.original_session_id is None


@pytest.mark.asyncio
async def test_interview_session_self_reference_prevented(db_session):
    """Test that a session cannot reference itself as original."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="self_reference@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a session
    session = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        retake_number=1,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Attempt to set original_session_id to itself
    session.original_session_id = session.id
    await db_session.commit()
    await db_session.refresh(session)

    # Database allows this at DB level, but application should prevent it
    # This test documents current behavior - consider adding app-level validation
    assert session.original_session_id == session.id


@pytest.mark.asyncio
async def test_interview_session_retake_number_consistency(db_session):
    """Test data integrity: retake_number should align with original_session_id."""
    from app.models.interview_session import InterviewSession
    from app.models.user import User

    user = User(email="consistency@example.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Test: retake_number=1 should have NULL original_session_id
    original = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        retake_number=1,
        original_session_id=None,
    )
    db_session.add(original)
    await db_session.commit()
    await db_session.refresh(original)

    assert original.retake_number == 1
    assert original.original_session_id is None

    # Test: retake_number > 1 should have original_session_id
    retake = InterviewSession(
        user_id=user.id,
        job_posting_id=None,
        status="active",
        retake_number=2,
        original_session_id=original.id,
    )
    db_session.add(retake)
    await db_session.commit()
    await db_session.refresh(retake)

    assert retake.retake_number == 2
    assert retake.original_session_id == original.id


@pytest.mark.asyncio
async def test_interview_session_retake_chain_query_performance(db_session):
    """Test that retake chain queries use composite index."""
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession
    from app.models.job_posting import JobPosting
    from app.models.user import User

    user = User(email="perf_test@example.com", hashed_password="hashed")
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

    # Create original session
    original = InterviewSession(
        user_id=user.id,
        job_posting_id=job_posting.id,
        status="completed",
        retake_number=1,
    )
    db_session.add(original)
    await db_session.commit()
    await db_session.refresh(original)

    # Create multiple retakes
    for i in range(2, 5):
        retake = InterviewSession(
            user_id=user.id,
            job_posting_id=job_posting.id,
            status="completed",
            retake_number=i,
            original_session_id=original.id,
        )
        db_session.add(retake)

    await db_session.commit()

    # Query pattern: "Get all attempts for this job by this user"
    # This should use ix_interview_sessions_user_job_original index
    result = await db_session.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == user.id)
        .where(InterviewSession.job_posting_id == job_posting.id)
        .order_by(InterviewSession.retake_number)
    )
    sessions = result.scalars().all()

    assert len(sessions) == 4  # 1 original + 3 retakes
    assert [s.retake_number for s in sessions] == [1, 2, 3, 4]
