"""
Tests for GET /api/v1/job-postings/{id} endpoint (detail).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_job_posting_success(async_client: AsyncClient, auth_headers: dict):
    """Test getting job posting by ID returns full details."""
    # Create job posting
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={
            "title": "Full Stack Developer",
            "company": "Tech Inc",
            "description": "We are looking for a full stack developer...",
            "experience_level": "Mid-level",
            "tech_stack": ["Python", "React"],
        },
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]

    # Get job posting by ID
    response = await async_client.get(
        f"/api/v1/job-postings/{job_posting_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_posting_id
    assert data["title"] == "Full Stack Developer"
    assert data["company"] == "Tech Inc"
    # Description should be included (unlike list endpoint)
    assert data["description"] == "We are looking for a full stack developer..."
    assert data["experience_level"] == "Mid-level"
    assert data["tech_stack"] == ["Python", "React"]


@pytest.mark.asyncio
async def test_get_job_posting_not_found_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test getting non-existent job posting returns 404."""
    import uuid

    fake_id = uuid.uuid4()
    response = await async_client.get(
        f"/api/v1/job-postings/{fake_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_job_posting_other_user_returns_404(
    async_client: AsyncClient, auth_headers: dict, db_session
):
    """Test getting another user's job posting returns 404."""
    from app.models.user import User
    from app.models.job_posting import JobPosting

    # Create another user with a job posting
    other_user = User(
        email="other-jp-detail@example.com",
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
    await db_session.refresh(other_job_posting)

    # Try to get other user's job posting
    response = await async_client.get(
        f"/api/v1/job-postings/{other_job_posting.id}",
        headers=auth_headers,
    )

    # Should return 404 (not reveal it exists)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_job_posting_unauthenticated_returns_401(
    async_client: AsyncClient,
):
    """Test unauthenticated request returns 401."""
    import uuid

    fake_id = uuid.uuid4()
    response = await async_client.get(f"/api/v1/job-postings/{fake_id}")
    assert response.status_code == 401
