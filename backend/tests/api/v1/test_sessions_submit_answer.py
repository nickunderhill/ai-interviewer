"""Tests for answer submission endpoint."""

import uuid

from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session_message import SessionMessage


@pytest.mark.asyncio
async def test_submit_answer_success(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test successful answer submission."""
    session_id = test_active_session["id"]
    answer_text = "I have 5 years of experience with Python, working on web applications using Django and FastAPI."

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": answer_text},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["message_type"] == "answer"
    assert data["content"] == answer_text
    assert data["question_type"] is None
    assert data["session_id"] == str(session_id)
    assert "created_at" in data
    assert "id" in data

    # Verify message stored in database
    result = await db_session.execute(select(SessionMessage).where(SessionMessage.id == uuid.UUID(data["id"])))
    message = result.scalar_one()
    assert message.content == answer_text
    assert message.message_type == "answer"


@pytest.mark.asyncio
async def test_submit_answer_empty_text(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
):
    """Test answer submission with empty text."""
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": ""},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_submit_answer_missing_text(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
):
    """Test answer submission without answer_text field."""
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_submit_answer_inactive_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session: dict,
):
    """Test cannot submit answer to completed session."""
    session_id = test_completed_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": "Test answer"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_ACTIVE"
    assert "Only active sessions accept answers" in data["detail"]["message"]


@pytest.mark.asyncio
async def test_submit_answer_paused_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_paused_session: dict,
):
    """Test cannot submit answer to paused session."""
    session_id = test_paused_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": "Test answer"},
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_ACTIVE"


@pytest.mark.asyncio
async def test_submit_answer_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test submitting answer to non-existent session."""
    fake_id = uuid.uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/answers",
        headers=auth_headers,
        json={"answer_text": "Test answer"},
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_submit_answer_unauthorized_session(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_session: dict,
):
    """Test cannot submit answer to another user's session."""
    session_id = other_user_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": "Test answer"},
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_submit_answer_unauthenticated(
    async_client: AsyncClient,
    test_active_session: dict,
):
    """Test submitting answer without authentication."""
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        json={"answer_text": "Test answer"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_submit_multiple_answers(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test submitting multiple answers to same session."""
    session_id = test_active_session["id"]

    # Submit first answer
    response1 = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": "First answer"},
    )
    assert response1.status_code == 201

    # Submit second answer
    response2 = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": "Second answer"},
    )
    assert response2.status_code == 201

    # Verify both stored
    result = await db_session.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == session_id,
            SessionMessage.message_type == "answer",
        )
    )
    answers = result.scalars().all()
    assert len(answers) == 2


@pytest.mark.asyncio
async def test_submit_long_answer(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test submitting a long answer."""
    session_id = test_active_session["id"]
    # Create a long answer (2000 characters)
    long_answer = "This is a detailed answer. " * 80

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers=auth_headers,
        json={"answer_text": long_answer},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == long_answer

    # Verify stored in database
    result = await db_session.execute(select(SessionMessage).where(SessionMessage.id == uuid.UUID(data["id"])))
    message = result.scalar_one()
    assert message.content == long_answer
