"""Tests for session messages retrieval endpoint."""

import uuid

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_get_messages_success(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_with_messages: dict,
):
    """Test retrieving messages in chronological order."""
    session_id = test_session_with_messages["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 2

    # Verify chronological order by created_at
    timestamps = [msg["created_at"] for msg in data]
    assert timestamps == sorted(timestamps)

    # Verify message types and fields
    for msg in data:
        assert msg["message_type"] in ["question", "answer"]
        assert "content" in msg
        if msg["message_type"] == "question":
            assert msg["question_type"] in ["technical", "behavioral", "situational"]
        else:
            assert msg["question_type"] is None


@pytest.mark.asyncio
async def test_get_messages_empty_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
):
    """Test retrieving messages from session with no messages."""
    session_id = test_active_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_messages_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test retrieving messages from non-existent session returns 404."""
    fake_id = uuid.uuid4()

    response = await async_client.get(
        f"/api/v1/sessions/{fake_id}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_messages_other_user(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_session: dict,
):
    """Test cannot retrieve other user's session messages."""
    session_id = other_user_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_messages_unauthenticated(
    async_client: AsyncClient,
    test_active_session: dict,
):
    """Test retrieving messages without authentication returns 401."""
    session_id = test_active_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
    )

    assert response.status_code == 401
