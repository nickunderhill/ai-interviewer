"""
Tests for PUT /api/v1/job-postings/{id} endpoint.
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_update_job_posting_success(async_client: AsyncClient, auth_headers: dict):
    """Test successful job posting update returns 200."""
    # Create job posting
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={
            "title": "Original Title",
            "description": "Original description",
            "company": "Old Company",
        },
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]

    # Update it
    updated_data = {
        "title": "Updated Title",
        "description": "Updated description with more details",
        "company": "New Company",
        "experience_level": "Senior",
        "tech_stack": ["Python", "FastAPI"],
    }

    response = await async_client.put(
        f"/api/v1/job-postings/{job_posting_id}",
        json=updated_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_posting_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description with more details"
    assert data["company"] == "New Company"
    assert data["experience_level"] == "Senior"
    assert data["tech_stack"] == ["Python", "FastAPI"]


@pytest.mark.asyncio
async def test_update_job_posting_timestamp_changes(async_client: AsyncClient, auth_headers: dict):
    """Test updated_at timestamp changes after update."""
    # Create job posting
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Original", "description": "Original"},
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    # Update it
    response = await async_client.put(
        f"/api/v1/job-postings/{job_posting_id}",
        json={"title": "Updated", "description": "Updated"},
        headers=auth_headers,
    )

    new_updated_at = response.json()["updated_at"]
    assert new_updated_at >= original_updated_at
    assert response.json()["title"] == "Updated"


@pytest.mark.asyncio
async def test_update_job_posting_not_found_returns_404(async_client: AsyncClient, auth_headers: dict):
    """Test updating non-existent job posting returns 404."""
    import uuid

    fake_id = uuid.uuid4()
    response = await async_client.put(
        f"/api/v1/job-postings/{fake_id}",
        json={"title": "Test", "description": "Test"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_job_posting_other_user_returns_404(async_client: AsyncClient, auth_headers: dict, db_session):
    """Test updating another user's job posting returns 404."""
    from app.models.job_posting import JobPosting
    from app.models.user import User

    # Create another user with a job posting
    other_user = User(
        email="other-update@example.com",
        hashed_password="hashed_pw",
    )
    db_session.add(other_user)
    await db_session.commit()
    await db_session.refresh(other_user)

    other_job_posting = JobPosting(
        user_id=other_user.id,
        title="Other User's Job",
        description="Description",
    )
    db_session.add(other_job_posting)
    await db_session.commit()
    await db_session.refresh(other_job_posting)

    # Try to update other user's job posting
    response = await async_client.put(
        f"/api/v1/job-postings/{other_job_posting.id}",
        json={"title": "Hacked", "description": "Hacked"},
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_job_posting_empty_title_returns_422(async_client: AsyncClient, auth_headers: dict):
    """Test updating with empty title returns 422."""
    # Create job posting
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Original", "description": "Original"},
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]

    # Try to update with empty title
    response = await async_client.put(
        f"/api/v1/job-postings/{job_posting_id}",
        json={"title": "", "description": "Description"},
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_job_posting_unauthenticated_returns_401(
    async_client: AsyncClient,
):
    """Test unauthenticated request returns 401."""
    import uuid

    fake_id = uuid.uuid4()
    response = await async_client.put(
        f"/api/v1/job-postings/{fake_id}",
        json={"title": "Test", "description": "Test"},
    )
    assert response.status_code == 401
