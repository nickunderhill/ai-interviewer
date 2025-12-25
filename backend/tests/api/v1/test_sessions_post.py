"""
Tests for POST /api/v1/sessions endpoint.
"""

import uuid

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_create_session_success(async_client: AsyncClient, auth_headers: dict, test_job_posting: dict):
    """Test successful session creation returns 201."""
    session_data = {
        "job_posting_id": str(test_job_posting["id"]),
    }

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"
    assert data["current_question_number"] == 0
    assert data["job_posting_id"] == str(test_job_posting["id"])
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data
    assert "job_posting" in data
    assert data["job_posting"]["id"] == str(test_job_posting["id"])
    assert data["job_posting"]["title"] == test_job_posting["title"]


@pytest.mark.asyncio
async def test_create_session_nonexistent_job_posting_returns_404(async_client: AsyncClient, auth_headers: dict):
    """Test session creation with non-existent job posting returns 404."""
    fake_id = str(uuid.uuid4())
    session_data = {
        "job_posting_id": fake_id,
    }

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "JOB_POSTING_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_session_other_users_job_posting_returns_404(
    async_client: AsyncClient, auth_headers: dict, other_user_job_posting: dict
):
    """Test creating session for another user's job posting returns 404."""
    session_data = {
        "job_posting_id": str(other_user_job_posting["id"]),
    }

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "JOB_POSTING_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_session_missing_job_posting_id_returns_422(async_client: AsyncClient, auth_headers: dict):
    """Test missing job_posting_id returns 422."""
    session_data = {}

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_session_invalid_uuid_returns_422(async_client: AsyncClient, auth_headers: dict):
    """Test invalid UUID format returns 422."""
    session_data = {
        "job_posting_id": "not-a-valid-uuid",
    }

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_session_unauthenticated_returns_401(async_client: AsyncClient):
    """Test creating session without authentication returns 401."""
    session_data = {
        "job_posting_id": str(uuid.uuid4()),
    }

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_session_persists_to_database(
    async_client: AsyncClient, auth_headers: dict, test_job_posting: dict, db_session
):
    """Test that created session is persisted to database."""
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    session_data = {
        "job_posting_id": str(test_job_posting["id"]),
    }

    response = await async_client.post(
        "/api/v1/sessions",
        json=session_data,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    session_id = data["id"]

    # Verify in database
    result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    db_session_obj = result.scalar_one_or_none()

    assert db_session_obj is not None
    assert str(db_session_obj.id) == session_id
    assert db_session_obj.status == "active"
    assert db_session_obj.current_question_number == 0
