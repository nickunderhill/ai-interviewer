"""
Tests for Resume model schema.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.resume import Resume
from app.models.user import User


@pytest.mark.asyncio
async def test_create_resume_with_user(db_session):
    """Test creating a resume associated with a user."""
    # Create user
    user = User(
        email="resume-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create resume
    resume = Resume(
        user_id=user.id,
        content="# My Resume\nExperience: 5 years in Python development",
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)

    # Verify
    assert resume.id is not None
    assert resume.user_id == user.id
    assert "Python development" in resume.content
    assert resume.created_at is not None
    assert resume.updated_at is not None


@pytest.mark.asyncio
async def test_one_to_one_relationship(db_session):
    """Test that user can have only one resume."""
    # Create user
    user = User(
        email="one-resume@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create first resume
    resume1 = Resume(
        user_id=user.id,
        content="First resume",
    )
    db_session.add(resume1)
    await db_session.commit()

    # Try to create second resume for same user - should fail due to unique constraint
    resume2 = Resume(
        user_id=user.id,
        content="Second resume",
    )
    db_session.add(resume2)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_cascading_delete(db_session):
    """Test that deleting user deletes their resume."""
    # Create user with resume
    user = User(
        email="cascade@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    resume = Resume(
        user_id=user.id,
        content="Will be deleted",
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)

    resume_id = resume.id

    # Delete user
    await db_session.delete(user)
    await db_session.commit()

    # Verify resume is also deleted
    result = await db_session.execute(select(Resume).where(Resume.id == resume_id))
    deleted_resume = result.scalar_one_or_none()
    assert deleted_resume is None


@pytest.mark.asyncio
async def test_content_field_accepts_large_text(db_session):
    """Test that content field can store large resume text."""
    user = User(
        email="large-resume@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create large content (> 10KB)
    large_content = "# Resume\n" + ("Experience detail. " * 1000)

    resume = Resume(
        user_id=user.id,
        content=large_content,
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)

    assert len(resume.content) > 10000
    assert resume.content == large_content


@pytest.mark.asyncio
async def test_timestamps_are_utc_aware(db_session):
    """Test that timestamps are UTC-aware."""
    user = User(
        email="timestamp-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    resume = Resume(
        user_id=user.id,
        content="Test content",
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)

    # Verify timezone awareness
    assert resume.created_at.tzinfo is not None
    assert resume.updated_at.tzinfo is not None
    # Verify UTC (offset should be 0)
    assert resume.created_at.utcoffset().total_seconds() == 0
    assert resume.updated_at.utcoffset().total_seconds() == 0


@pytest.mark.asyncio
async def test_user_resume_relationship(db_session):
    """Test bidirectional relationship between User and Resume."""
    user = User(
        email="relationship-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    resume = Resume(
        user_id=user.id,
        content="Test resume content",
    )
    db_session.add(resume)
    await db_session.commit()
    await db_session.refresh(resume)

    # Load user with relationship
    result = await db_session.execute(select(User).where(User.id == user.id))
    loaded_user = result.scalar_one()

    # Access relationship (lazy load)
    await db_session.refresh(loaded_user, ["resume"])
    assert loaded_user.resume is not None
    assert loaded_user.resume.content == "Test resume content"

    # Access reverse relationship (both directions verified)
    await db_session.refresh(resume, ["user"])
    assert resume.user is not None
    assert resume.user.email == "relationship-test@example.com"
    assert resume.user.id == user.id
