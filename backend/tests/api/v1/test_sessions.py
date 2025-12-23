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


@pytest.mark.asyncio
async def test_complete_active_session_success(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(session_id)
    assert data["status"] == "completed"

    result = await db_session.execute(
        select(InterviewSession).where(InterviewSession.id == UUID(str(session_id)))
    )
    session = result.scalar_one()
    assert session.status == "completed"


@pytest.mark.asyncio
async def test_complete_paused_session_success(
    async_client: AsyncClient,
    auth_headers: dict,
    test_paused_session: dict,
):
    session_id = test_paused_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(session_id)
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_complete_completed_session_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session: dict,
):
    session_id = test_completed_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_ALREADY_COMPLETED"


@pytest.mark.asyncio
async def test_complete_session_appears_in_completed_list_not_active_list(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
):
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200

    active_resp = await async_client.get(
        "/api/v1/sessions?status=active",
        headers=auth_headers,
    )
    assert active_resp.status_code == 200
    active = active_resp.json()
    assert not any(s["id"] == str(session_id) for s in active)

    completed_resp = await async_client.get(
        "/api/v1/sessions?status=completed",
        headers=auth_headers,
    )
    assert completed_resp.status_code == 200
    completed = completed_resp.json()
    assert any(s["id"] == str(session_id) for s in completed)


@pytest.mark.asyncio
async def test_complete_session_preserves_messages(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    session_id = test_active_session["id"]

    db_session.add(
        SessionMessage(
            session_id=session_id,
            message_type="question",
            content="Pre-completion question",
            question_type="technical",
        )
    )
    await db_session.commit()

    before_resp = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
    )
    assert before_resp.status_code == 200
    messages_before = before_resp.json()

    complete_resp = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers=auth_headers,
    )
    assert complete_resp.status_code == 200

    after_resp = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers=auth_headers,
    )
    assert after_resp.status_code == 200
    messages_after = after_resp.json()

    assert messages_after == messages_before


@pytest.mark.asyncio
async def test_complete_session_not_found(
    async_client: AsyncClient,
    auth_headers: dict,
):
    fake_id = uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_complete_session_other_user_fails(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_session: dict,
):
    response = await async_client.post(
        f"/api/v1/sessions/{other_user_session['id']}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_complete_session_unauthenticated_fails(
    async_client: AsyncClient,
    test_active_session: dict,
):
    session_id = test_active_session["id"]

    response = await async_client.post(f"/api/v1/sessions/{session_id}/complete")
    assert response.status_code == 401
