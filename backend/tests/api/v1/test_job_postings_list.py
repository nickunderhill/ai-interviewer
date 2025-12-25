"""
Tests for GET /api/v1/job-postings endpoint (list).
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_list_job_postings_success(async_client: AsyncClient, auth_headers: dict):
    """Test listing job postings returns array."""
    # Create two job postings
    await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Position 1", "description": "Description 1"},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Position 2", "description": "Description 2"},
        headers=auth_headers,
    )

    # List them
    response = await async_client.get(
        "/api/v1/job-postings/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    # Verify list items don't include description (performance optimization)
    assert "description" not in data[0]
    assert "title" in data[0]
    assert "id" in data[0]


@pytest.mark.asyncio
async def test_list_job_postings_empty_returns_empty_array(async_client: AsyncClient, auth_headers: dict):
    """Test listing with no job postings returns empty array."""
    response = await async_client.get(
        "/api/v1/job-postings/",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_job_postings_ordered_by_created_at_desc(async_client: AsyncClient, auth_headers: dict):
    """Test job postings are ordered by created_at DESC (newest first)."""
    # Create job postings in sequence
    await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "First Post", "description": "Description"},
        headers=auth_headers,
    )
    await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Second Post", "description": "Description"},
        headers=auth_headers,
    )

    # List them
    response = await async_client.get(
        "/api/v1/job-postings/",
        headers=auth_headers,
    )

    data = response.json()
    # Second post should come first (newest first)
    assert data[0]["title"] == "Second Post"
    assert data[1]["title"] == "First Post"


@pytest.mark.asyncio
async def test_list_job_postings_user_isolation(async_client: AsyncClient, auth_headers: dict, db_session):
    """Test users can only see their own job postings."""
    from app.models.job_posting import JobPosting
    from app.models.user import User

    # Create another user with a job posting
    other_user = User(
        email="other-jp@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_job_posting = JobPosting(
        user_id=other_user.id,
        title="Other User's Job",
        description="Secret job posting",
    )
    db_session.add(other_job_posting)
    await db_session.commit()

    # Create job posting for test user
    await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Test User's Job", "description": "Description"},
        headers=auth_headers,
    )

    # List job postings
    response = await async_client.get(
        "/api/v1/job-postings/",
        headers=auth_headers,
    )

    data = response.json()
    # Should only see test user's job posting
    assert len(data) == 1
    assert data[0]["title"] == "Test User's Job"


@pytest.mark.asyncio
async def test_list_job_postings_unauthenticated_returns_401(
    async_client: AsyncClient,
):
    """Test unauthenticated request returns 401."""
    response = await async_client.get("/api/v1/job-postings/")
    assert response.status_code == 401
