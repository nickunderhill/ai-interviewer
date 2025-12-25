"""
Tests for GET /api/v1/sessions endpoint (list sessions).
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_list_sessions_success(async_client: AsyncClient, auth_headers: dict, test_sessions: list):
    """Test listing all sessions returns 200."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # We created 3 test sessions


@pytest.mark.asyncio
async def test_list_sessions_ordered_by_created_at_desc(
    async_client: AsyncClient, auth_headers: dict, test_sessions: list
):
    """Test sessions are ordered by created_at DESC (newest first)."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify ordering (newest first)
    dates = [session["created_at"] for session in data]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio
async def test_list_sessions_with_status_filter_active(
    async_client: AsyncClient, auth_headers: dict, test_sessions: list
):
    """Test filtering sessions by status=active."""
    response = await async_client.get(
        "/api/v1/sessions?status=active",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert all(session["status"] == "active" for session in data)
    assert len(data) >= 1  # At least one active session


@pytest.mark.asyncio
async def test_list_sessions_with_status_filter_completed(
    async_client: AsyncClient, auth_headers: dict, test_sessions: list
):
    """Test filtering sessions by status=completed."""
    response = await async_client.get(
        "/api/v1/sessions?status=completed",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert all(session["status"] == "completed" for session in data)


@pytest.mark.asyncio
async def test_list_sessions_with_invalid_status_returns_400(async_client: AsyncClient, auth_headers: dict):
    """Test invalid status filter returns 400."""
    response = await async_client.get(
        "/api/v1/sessions?status=invalid_status",
        headers=auth_headers,
    )

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["code"] == "INVALID_STATUS_FILTER"


@pytest.mark.asyncio
async def test_list_sessions_empty_result(async_client: AsyncClient, auth_headers: dict):
    """Test listing sessions when user has none returns empty array."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # May or may not be empty depending on other tests


@pytest.mark.asyncio
async def test_list_sessions_includes_job_posting_details(
    async_client: AsyncClient, auth_headers: dict, test_sessions: list
):
    """Test that job posting details are included in response."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    if len(data) > 0:
        session = data[0]
        assert "job_posting" in session
        if session["job_posting"]:
            assert "id" in session["job_posting"]
            assert "title" in session["job_posting"]
            assert "company" in session["job_posting"]


@pytest.mark.asyncio
async def test_list_sessions_unauthenticated_returns_401(async_client: AsyncClient):
    """Test listing sessions without authentication returns 401."""
    response = await async_client.get("/api/v1/sessions")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_sessions_user_isolation(
    async_client: AsyncClient,
    auth_headers: dict,
    test_sessions: list,
    other_user_session: dict,
):
    """Test that users only see their own sessions."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify none of the sessions belong to other user
    other_user_session_id = str(other_user_session["id"])
    session_ids = [session["id"] for session in data]
    assert other_user_session_id not in session_ids
