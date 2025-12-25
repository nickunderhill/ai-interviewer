"""
Tests for DELETE /api/v1/job-postings/{id} endpoint.
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_delete_job_posting_success(async_client: AsyncClient, auth_headers: dict):
    """Test successful deletion returns 204."""
    # Create job posting
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "To Delete", "description": "Will be deleted"},
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]

    # Delete it
    response = await async_client.delete(
        f"/api/v1/job-postings/{job_posting_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.asyncio
async def test_get_after_delete_returns_404(async_client: AsyncClient, auth_headers: dict):
    """Test getting job posting after deletion returns 404."""
    # Create job posting
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "To Delete", "description": "Will be deleted"},
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]

    # Verify it exists
    get_response = await async_client.get(
        f"/api/v1/job-postings/{job_posting_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 200

    # Delete it
    delete_response = await async_client.delete(
        f"/api/v1/job-postings/{job_posting_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204

    # Try to get it again
    get_after_delete = await async_client.get(
        f"/api/v1/job-postings/{job_posting_id}",
        headers=auth_headers,
    )
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_posting_not_found_returns_404(async_client: AsyncClient, auth_headers: dict):
    """Test deleting non-existent job posting returns 404."""
    import uuid

    fake_id = uuid.uuid4()
    response = await async_client.delete(
        f"/api/v1/job-postings/{fake_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_posting_other_user_returns_404(async_client: AsyncClient, auth_headers: dict, db_session):
    """Test deleting another user's job posting returns 404."""
    from app.models.job_posting import JobPosting
    from app.models.user import User

    # Create another user with a job posting
    other_user = User(
        email="other-delete@example.com",
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

    # Try to delete other user's job posting
    response = await async_client.delete(
        f"/api/v1/job-postings/{other_job_posting.id}",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_job_posting_unauthenticated_returns_401(
    async_client: AsyncClient,
):
    """Test unauthenticated request returns 401."""
    import uuid

    fake_id = uuid.uuid4()
    response = await async_client.delete(f"/api/v1/job-postings/{fake_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_recreate_after_delete(async_client: AsyncClient, auth_headers: dict):
    """Test user can create new job posting after deleting one."""
    # Create and delete
    create_response = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "First", "description": "First"},
        headers=auth_headers,
    )
    job_posting_id = create_response.json()["id"]

    await async_client.delete(
        f"/api/v1/job-postings/{job_posting_id}",
        headers=auth_headers,
    )

    # Create another one
    create_response2 = await async_client.post(
        "/api/v1/job-postings/",
        json={"title": "Second", "description": "Second after deletion"},
        headers=auth_headers,
    )

    assert create_response2.status_code == 201
    assert create_response2.json()["title"] == "Second"
