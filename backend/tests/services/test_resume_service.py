"""
Tests for resume service business logic.
"""


import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.resume_service import ResumeConflictException, create_resume


@pytest.mark.asyncio
async def test_create_resume_success(db_session: AsyncSession):
    """Test successful resume creation."""
    # Create user
    user = User(
        email="resume-service-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create resume
    content = "# Professional Resume\nExperience: 10 years"
    resume = await create_resume(db_session, user.id, content)

    assert resume.id is not None
    assert resume.user_id == user.id
    assert resume.content == content
    assert resume.created_at is not None
    assert resume.updated_at is not None


@pytest.mark.asyncio
async def test_create_resume_duplicate_raises_conflict(db_session: AsyncSession):
    """Test creating duplicate resume raises ResumeConflictException."""
    # Create user
    user = User(
        email="duplicate-resume-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create first resume
    await create_resume(db_session, user.id, "First resume content")

    # Attempt to create second resume (should raise exception)
    with pytest.raises(ResumeConflictException) as exc_info:
        await create_resume(db_session, user.id, "Second resume content")

    assert exc_info.value.status_code == 409
    assert "already has a resume" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_resume_for_different_users(db_session: AsyncSession):
    """Test creating resumes for different users succeeds."""
    # Create two users
    user1 = User(email="user1@example.com", hashed_password="hashed_pw")
    user2 = User(email="user2@example.com", hashed_password="hashed_pw")
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    # Create resumes for both users
    resume1 = await create_resume(db_session, user1.id, "Resume 1 content")
    resume2 = await create_resume(db_session, user2.id, "Resume 2 content")

    assert resume1.user_id == user1.id
    assert resume2.user_id == user2.id
    assert resume1.id != resume2.id


@pytest.mark.asyncio
async def test_create_resume_with_large_content(db_session: AsyncSession):
    """Test creating resume with large content."""
    user = User(email="large-content-test@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create large content (close to 50KB limit)
    large_content = "Professional Experience:\n" + ("Detail. " * 6000)

    resume = await create_resume(db_session, user.id, large_content)

    assert resume.content == large_content
    assert len(resume.content) > 40000


@pytest.mark.asyncio
async def test_get_user_resume_returns_resume(db_session: AsyncSession):
    """Test retrieving existing resume."""
    from app.services.resume_service import get_user_resume

    user = User(email="get-test@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create resume
    created = await create_resume(db_session, user.id, "Test content")

    # Retrieve it
    retrieved = await get_user_resume(db_session, user.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.content == "Test content"


@pytest.mark.asyncio
async def test_get_user_resume_returns_none_when_missing(db_session: AsyncSession):
    """Test retrieving non-existent resume returns None."""
    from app.services.resume_service import get_user_resume

    user = User(email="no-resume@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Don't create resume
    result = await get_user_resume(db_session, user.id)

    assert result is None


@pytest.mark.asyncio
async def test_update_user_resume_updates_content_and_timestamp(
    db_session: AsyncSession,
):
    """Test updating resume content and timestamp."""
    from app.services.resume_service import update_user_resume

    user = User(email="update-test@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create resume
    original = await create_resume(db_session, user.id, "Original content")
    original_updated_at = original.updated_at

    # Update it
    updated = await update_user_resume(db_session, user.id, "Updated content")

    assert updated.id == original.id
    assert updated.content == "Updated content"
    assert updated.updated_at >= original_updated_at
    assert updated.created_at == original.created_at


@pytest.mark.asyncio
async def test_update_user_resume_raises_not_found(db_session: AsyncSession):
    """Test updating non-existent resume raises exception."""
    from app.services.resume_service import (
        ResumeNotFoundException,
        update_user_resume,
    )

    user = User(email="no-resume-update@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Don't create resume, try to update
    with pytest.raises(ResumeNotFoundException) as exc_info:
        await update_user_resume(db_session, user.id, "New content")

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_resume_removes_resume(db_session: AsyncSession):
    """Test deleting resume removes it from database."""
    from app.services.resume_service import delete_user_resume, get_user_resume

    user = User(email="delete-test@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create resume
    await create_resume(db_session, user.id, "To be deleted")

    # Delete it
    await delete_user_resume(db_session, user.id)

    # Verify it's gone
    result = await get_user_resume(db_session, user.id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_user_resume_raises_not_found(db_session: AsyncSession):
    """Test deleting non-existent resume raises exception."""
    from app.services.resume_service import (
        ResumeNotFoundException,
        delete_user_resume,
    )

    user = User(email="no-resume-delete@example.com", hashed_password="hashed_pw")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Don't create resume, try to delete
    with pytest.raises(ResumeNotFoundException) as exc_info:
        await delete_user_resume(db_session, user.id)

    assert exc_info.value.status_code == 404
