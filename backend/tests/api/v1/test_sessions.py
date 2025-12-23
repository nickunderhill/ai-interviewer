"""Tests for session pause/resume and session detail resume context."""

import pytest
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_session import InterviewSession
from app.models.session_message import SessionMessage


@pytest.mark.asyncio
async def test_pause_session_success(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    session_id = test_active_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/pause",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(session_id)
    assert data["status"] == "paused"

    # Verify in database
    result = await db_session.execute(
        select(InterviewSession).where(InterviewSession.id == UUID(str(session_id)))
    )
    session = result.scalar_one()
    assert session.status == "paused"


@pytest.mark.asyncio
async def test_pause_session_completed_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session: dict,
):
    session_id = test_completed_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/pause",
        headers=auth_headers,
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_SESSION_STATE"


@pytest.mark.asyncio
async def test_pause_session_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    fake_id = uuid4()

    response = await async_client.put(
        f"/api/v1/sessions/{fake_id}/pause",
        headers=auth_headers,
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_pause_session_other_user_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_session: dict,
):
    response = await async_client.put(
        f"/api/v1/sessions/{other_user_session['id']}/pause",
        headers=auth_headers,
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_pause_session_unauthenticated_fails(
    async_client: AsyncClient,
    test_active_session: dict,
):
    session_id = test_active_session["id"]

    response = await async_client.put(f"/api/v1/sessions/{session_id}/pause")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resume_session_success(
    async_client: AsyncClient,
    auth_headers: dict,
    test_paused_session: dict,
):
    session_id = test_paused_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(session_id)
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_resume_session_active_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
):
    session_id = test_active_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers=auth_headers,
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_SESSION_STATE"


@pytest.mark.asyncio
async def test_resume_session_completed_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session: dict,
):
    session_id = test_completed_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers=auth_headers,
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "INVALID_SESSION_STATE"


@pytest.mark.asyncio
async def test_resume_session_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    fake_id = uuid4()

    response = await async_client.put(
        f"/api/v1/sessions/{fake_id}/resume",
        headers=auth_headers,
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_resume_session_other_user_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_session: dict,
):
    response = await async_client.put(
        f"/api/v1/sessions/{other_user_session['id']}/resume",
        headers=auth_headers,
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_resume_session_unauthenticated_fails(
    async_client: AsyncClient,
    test_paused_session: dict,
):
    session_id = test_paused_session["id"]

    response = await async_client.put(f"/api/v1/sessions/{session_id}/resume")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_session_detail_provides_full_context(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_with_resume: dict,
    db_session: AsyncSession,
):
    session_id = test_session_with_resume["id"]

    db_session.add(
        SessionMessage(
            session_id=session_id,
            message_type="question",
            content="Test question?",
            question_type="technical",
        )
    )
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(session_id)
    assert data["job_posting"] is not None
    assert data["resume"] is not None

    assert "messages" in data
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) >= 1
