"""
Tests for job_posting_service module.
"""

import pytest

from app.models.user import User
from app.services import job_posting_service
from app.services.job_posting_service import JobPostingNotFoundException


@pytest.mark.asyncio
async def test_create_job_posting_success(db_session):
    """Test creating job posting with all fields."""
    user = User(email="user@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    job_posting = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Senior Python Developer",
        description="Looking for experienced Python developer",
        company="Tech Corp",
        experience_level="Senior",
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
    )

    assert job_posting.id is not None
    assert job_posting.user_id == user.id
    assert job_posting.title == "Senior Python Developer"
    assert job_posting.description == "Looking for experienced Python developer"
    assert job_posting.company == "Tech Corp"
    assert job_posting.experience_level == "Senior"
    assert job_posting.tech_stack == ["Python", "FastAPI", "PostgreSQL"]


@pytest.mark.asyncio
async def test_create_job_posting_only_required_fields(db_session):
    """Test creating job posting with only required fields."""
    user = User(email="user2@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    job_posting = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Junior Developer",
        description="Entry level position",
    )

    assert job_posting.id is not None
    assert job_posting.title == "Junior Developer"
    assert job_posting.description == "Entry level position"
    assert job_posting.company is None
    assert job_posting.experience_level is None
    assert job_posting.tech_stack is None or job_posting.tech_stack == []


@pytest.mark.asyncio
async def test_get_user_job_postings_returns_list(db_session):
    """Test get_user_job_postings returns list of postings."""
    user = User(email="user3@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create multiple job postings
    await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Job 1",
        description="Description 1",
    )
    await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Job 2",
        description="Description 2",
    )

    job_postings = await job_posting_service.get_user_job_postings(
        db=db_session, user_id=user.id
    )

    assert len(job_postings) == 2
    assert job_postings[0].title in ["Job 1", "Job 2"]


@pytest.mark.asyncio
async def test_get_user_job_postings_empty_list(db_session):
    """Test get_user_job_postings returns empty list when no postings."""
    user = User(email="user4@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    job_postings = await job_posting_service.get_user_job_postings(
        db=db_session, user_id=user.id
    )

    assert job_postings == []


@pytest.mark.asyncio
async def test_get_user_job_postings_ordered_by_created_at_desc(db_session):
    """Test job postings are ordered by created_at descending."""
    user = User(email="user5@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create postings in order
    first = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="First Job",
        description="First",
    )
    second = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Second Job",
        description="Second",
    )

    job_postings = await job_posting_service.get_user_job_postings(
        db=db_session, user_id=user.id
    )

    # Most recent should be first
    assert job_postings[0].id == second.id
    assert job_postings[1].id == first.id


@pytest.mark.asyncio
async def test_get_user_job_postings_user_isolation(db_session):
    """Test user can only see their own job postings."""
    user1 = User(email="user6@test.com", hashed_password="hashed")
    user2 = User(email="user7@test.com", hashed_password="hashed")
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    # Create postings for both users
    await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user1.id,
        title="User 1 Job",
        description="Description",
    )
    await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user2.id,
        title="User 2 Job",
        description="Description",
    )

    user1_postings = await job_posting_service.get_user_job_postings(
        db=db_session, user_id=user1.id
    )

    assert len(user1_postings) == 1
    assert user1_postings[0].title == "User 1 Job"


@pytest.mark.asyncio
async def test_get_job_posting_by_id_returns_posting(db_session):
    """Test get_job_posting_by_id returns correct posting."""
    user = User(email="user8@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    created = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Test Job",
        description="Description",
    )

    retrieved = await job_posting_service.get_job_posting_by_id(
        db=db_session, job_posting_id=created.id, user_id=user.id
    )

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.title == "Test Job"


@pytest.mark.asyncio
async def test_get_job_posting_by_id_wrong_user_raises_exception(db_session):
    """Test get_job_posting_by_id raises exception for wrong user."""
    user1 = User(email="user9@test.com", hashed_password="hashed")
    user2 = User(email="user10@test.com", hashed_password="hashed")
    db_session.add_all([user1, user2])
    await db_session.commit()
    await db_session.refresh(user1)
    await db_session.refresh(user2)

    created = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user1.id,
        title="User 1 Job",
        description="Description",
    )

    # Try to get with wrong user - should raise exception
    with pytest.raises(JobPostingNotFoundException) as exc_info:
        await job_posting_service.get_job_posting_by_id(
            db=db_session, job_posting_id=created.id, user_id=user2.id
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_get_job_posting_by_id_nonexistent_raises_exception(db_session):
    """Test get_job_posting_by_id raises exception for non-existent posting."""
    import uuid

    user = User(email="user11@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    fake_id = uuid.uuid4()

    with pytest.raises(JobPostingNotFoundException) as exc_info:
        await job_posting_service.get_job_posting_by_id(
            db=db_session, job_posting_id=fake_id, user_id=user.id
        )

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_update_job_posting_updates_fields(db_session):
    """Test update_job_posting updates all fields."""
    user = User(email="user12@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    created = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="Original",
        description="Original description",
    )
    original_updated_at = created.updated_at

    updated = await job_posting_service.update_job_posting(
        db=db_session,
        job_posting_id=created.id,
        user_id=user.id,
        title="Updated Title",
        description="Updated description",
        company="New Company",
        experience_level="Senior",
        tech_stack=["Python"],
    )

    assert updated.title == "Updated Title"
    assert updated.description == "Updated description"
    assert updated.company == "New Company"
    assert updated.experience_level == "Senior"
    assert updated.tech_stack == ["Python"]
    assert updated.updated_at >= original_updated_at


@pytest.mark.asyncio
async def test_update_job_posting_not_found_raises_exception(db_session):
    """Test update_job_posting raises exception for non-existent posting."""
    import uuid

    user = User(email="user13@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    fake_id = uuid.uuid4()

    with pytest.raises(JobPostingNotFoundException) as exc_info:
        await job_posting_service.update_job_posting(
            db=db_session,
            job_posting_id=fake_id,
            user_id=user.id,
            title="Test",
            description="Test",
        )

    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail).lower()


@pytest.mark.asyncio
async def test_delete_job_posting_deletes_successfully(db_session):
    """Test delete_job_posting removes posting from database."""
    user = User(email="user14@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    created = await job_posting_service.create_job_posting(
        db=db_session,
        user_id=user.id,
        title="To Delete",
        description="Will be deleted",
    )

    # Verify exists
    retrieved = await job_posting_service.get_job_posting_by_id(
        db=db_session, job_posting_id=created.id, user_id=user.id
    )
    assert retrieved is not None

    # Delete
    await job_posting_service.delete_job_posting(
        db=db_session, job_posting_id=created.id, user_id=user.id
    )

    # Verify deleted - should raise exception now
    with pytest.raises(JobPostingNotFoundException):
        await job_posting_service.get_job_posting_by_id(
            db=db_session, job_posting_id=created.id, user_id=user.id
        )


@pytest.mark.asyncio
async def test_delete_job_posting_not_found_raises_exception(db_session):
    """Test delete_job_posting raises exception for non-existent posting."""
    import uuid

    user = User(email="user15@test.com", hashed_password="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    fake_id = uuid.uuid4()

    with pytest.raises(JobPostingNotFoundException) as exc_info:
        await job_posting_service.delete_job_posting(
            db=db_session, job_posting_id=fake_id, user_id=user.id
        )

    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail).lower()
