"""
Tests for JobPosting model schema.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.job_posting import JobPosting
from app.models.user import User


@pytest.mark.asyncio
async def test_create_job_posting_with_user(db_session):
    """Test creating a job posting associated with a user."""
    # Create user
    user = User(
        email="job-posting-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create job posting
    job_posting = JobPosting(
        user_id=user.id,
        title="Senior Python Developer",
        company="Tech Corp",
        description="We are looking for a Senior Python Developer...",
        experience_level="Senior",
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    # Verify
    assert job_posting.id is not None
    assert job_posting.user_id == user.id
    assert job_posting.title == "Senior Python Developer"
    assert job_posting.company == "Tech Corp"
    assert "Python Developer" in job_posting.description
    assert job_posting.experience_level == "Senior"
    assert job_posting.tech_stack == ["Python", "FastAPI", "PostgreSQL"]
    assert job_posting.created_at is not None
    assert job_posting.updated_at is not None


@pytest.mark.asyncio
async def test_one_to_many_relationship(db_session):
    """Test that user can have multiple job postings."""
    # Create user
    user = User(
        email="multiple-jobs@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create multiple job postings
    job1 = JobPosting(
        user_id=user.id,
        title="Frontend Developer",
        description="React position",
    )
    job2 = JobPosting(
        user_id=user.id,
        title="Backend Developer",
        description="FastAPI position",
    )
    db_session.add_all([job1, job2])
    await db_session.commit()

    # Query all job postings for user
    result = await db_session.execute(select(JobPosting).where(JobPosting.user_id == user.id))
    job_postings = result.scalars().all()

    assert len(job_postings) == 2
    titles = [jp.title for jp in job_postings]
    assert "Frontend Developer" in titles
    assert "Backend Developer" in titles


@pytest.mark.asyncio
async def test_required_fields(db_session):
    """Test that required fields (title, description) must be present."""
    user = User(
        email="required-fields@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Try to create without title (should fail)
    job_posting = JobPosting(
        user_id=user.id,
        description="Description without title",
    )
    db_session.add(job_posting)

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_optional_fields_can_be_null(db_session):
    """Test that optional fields (company, experience_level, tech_stack) can be null."""
    user = User(
        email="optional-fields@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create with only required fields
    job_posting = JobPosting(
        user_id=user.id,
        title="Developer Position",
        description="Some description",
        # company, experience_level, tech_stack omitted
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    assert job_posting.company is None
    assert job_posting.experience_level is None
    assert job_posting.tech_stack is None


@pytest.mark.asyncio
async def test_description_field_accepts_large_text(db_session):
    """Test that description field can store large job descriptions."""
    user = User(
        email="large-description@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create large description (> 5KB)
    large_description = "Job Description:\n" + ("Detailed requirement. " * 500)

    job_posting = JobPosting(
        user_id=user.id,
        title="Test Position",
        description=large_description,
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    assert len(job_posting.description) > 5000
    assert job_posting.description == large_description


@pytest.mark.asyncio
async def test_tech_stack_jsonb_storage(db_session):
    """Test tech_stack JSONB storage and retrieval."""
    user = User(
        email="tech-stack-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create with tech stack array
    tech_stack = ["Python", "React", "PostgreSQL", "Docker", "Kubernetes"]
    job_posting = JobPosting(
        user_id=user.id,
        title="Full Stack Developer",
        description="Full stack position",
        tech_stack=tech_stack,
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    # Verify JSONB storage works correctly
    assert job_posting.tech_stack == tech_stack
    assert isinstance(job_posting.tech_stack, list)
    assert len(job_posting.tech_stack) == 5
    assert "Python" in job_posting.tech_stack


@pytest.mark.asyncio
async def test_timestamps_are_utc_aware(db_session):
    """Test that timestamps are UTC-aware."""
    user = User(
        email="timestamp-test-jp@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    job_posting = JobPosting(
        user_id=user.id,
        title="Test Position",
        description="Test content",
    )
    db_session.add(job_posting)
    await db_session.commit()
    await db_session.refresh(job_posting)

    # Verify timezone awareness
    assert job_posting.created_at.tzinfo is not None
    assert job_posting.updated_at.tzinfo is not None
    # Verify UTC (offset should be 0)
    assert job_posting.created_at.utcoffset().total_seconds() == 0
    assert job_posting.updated_at.utcoffset().total_seconds() == 0


@pytest.mark.asyncio
async def test_cascading_delete(db_session):
    """Test that deleting user deletes their job postings."""
    # Create user with job postings
    user = User(
        email="cascade-jp@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    job1 = JobPosting(
        user_id=user.id,
        title="Job 1",
        description="Will be deleted",
    )
    job2 = JobPosting(
        user_id=user.id,
        title="Job 2",
        description="Will be deleted too",
    )
    db_session.add_all([job1, job2])
    await db_session.commit()
    await db_session.refresh(job1)
    await db_session.refresh(job2)

    job1_id = job1.id
    job2_id = job2.id

    # Delete user
    await db_session.delete(user)
    await db_session.commit()

    # Verify job postings are also deleted
    result = await db_session.execute(select(JobPosting).where(JobPosting.id.in_([job1_id, job2_id])))
    deleted_jobs = result.scalars().all()
    assert len(deleted_jobs) == 0


@pytest.mark.asyncio
async def test_user_job_postings_relationship(db_session):
    """Test bidirectional relationship between User and JobPostings."""
    user = User(
        email="relationship-jp-test@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create job postings
    job1 = JobPosting(
        user_id=user.id,
        title="Position 1",
        description="Description 1",
    )
    job2 = JobPosting(
        user_id=user.id,
        title="Position 2",
        description="Description 2",
    )
    db_session.add_all([job1, job2])
    await db_session.commit()

    # Load user with relationship
    result = await db_session.execute(select(User).where(User.id == user.id))
    loaded_user = result.scalar_one()

    # Access relationship (lazy load)
    await db_session.refresh(loaded_user, ["job_postings"])
    assert loaded_user.job_postings is not None
    assert len(loaded_user.job_postings) == 2

    # Access reverse relationship
    await db_session.refresh(job1, ["user"])
    assert job1.user is not None
    assert job1.user.email == "relationship-jp-test@example.com"
