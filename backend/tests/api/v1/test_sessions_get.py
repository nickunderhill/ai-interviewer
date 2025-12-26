"""
Tests for GET /api/v1/sessions/{id} endpoint (session detail).
"""

import uuid

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_get_session_detail_success(
    async_client: AsyncClient, auth_headers: dict, test_session_with_resume: dict
):
    """Test retrieving full session details returns 200."""
    session_id = test_session_with_resume["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(session_id)
    assert data["status"] in ["active", "paused", "completed"]
    assert "id" in data
    assert "user_id" in data
    assert "job_posting_id" in data
    assert "status" in data
    assert "current_question_number" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_session_detail_includes_job_posting(
    async_client: AsyncClient, auth_headers: dict, test_session_with_resume: dict
):
    """Test that job posting details are included in response."""
    session_id = test_session_with_resume["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "job_posting" in data
    if data["job_posting"]:
        assert "id" in data["job_posting"]
        assert "title" in data["job_posting"]
        assert "company" in data["job_posting"]
        assert "description" in data["job_posting"]
        assert "experience_level" in data["job_posting"]
        assert "tech_stack" in data["job_posting"]


@pytest.mark.asyncio
async def test_get_session_detail_includes_resume(
    async_client: AsyncClient, auth_headers: dict, test_session_with_resume: dict
):
    """Test that resume content is included in response."""
    session_id = test_session_with_resume["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert "resume" in data
    if data["resume"]:
        assert "id" in data["resume"]
        assert "content" in data["resume"]


@pytest.mark.asyncio
async def test_get_session_detail_includes_retake_fields(
    async_client: AsyncClient, auth_headers: dict, test_session_with_resume: dict
):
    """Test that retake tracking fields are included in session detail response."""
    session_id = test_session_with_resume["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify retake fields are present
    assert "retake_number" in data
    assert "original_session_id" in data
    assert isinstance(data["retake_number"], int)
    assert data["retake_number"] >= 1


@pytest.mark.asyncio
async def test_get_session_detail_handles_missing_resume(
    async_client: AsyncClient, auth_headers: dict, test_session_no_resume: dict
):
    """Test session detail when user hasn't uploaded resume."""
    session_id = test_session_no_resume["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resume"] is None


@pytest.mark.asyncio
async def test_get_session_detail_not_found_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test retrieving non-existent session returns 404."""
    fake_id = uuid.uuid4()

    response = await async_client.get(
        f"/api/v1/sessions/{fake_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_session_detail_other_user_returns_404(
    async_client: AsyncClient, auth_headers: dict, other_user_session: dict
):
    """Test retrieving another user's session returns 404."""
    session_id = other_user_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_session_detail_invalid_uuid_returns_422(
    async_client: AsyncClient, auth_headers: dict
):
    """Test invalid UUID format returns 422."""
    response = await async_client.get(
        "/api/v1/sessions/not-a-valid-uuid",
        headers=auth_headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_session_detail_unauthenticated_returns_401(
    async_client: AsyncClient, test_session_with_resume: dict
):
    """Test getting session detail without authentication returns 401."""
    session_id = test_session_with_resume["id"]

    response = await async_client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 401
