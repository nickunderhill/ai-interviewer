"""
Tests for POST /api/v1/sessions/{id}/retake endpoint.
"""

import uuid

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_create_retake_success_first_retake(
    async_client: AsyncClient, auth_headers: dict, test_session_completed, db_session
):
    """Test creating first retake from original session."""
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    response = await async_client.post(
        f"/api/v1/sessions/{test_session_completed.id}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    # Verify response structure
    assert "id" in data
    assert data["retake_number"] == 2
    assert data["original_session_id"] == str(test_session_completed.id)
    assert data["status"] == "active"
    assert data["current_question_number"] == 0
    assert data["job_posting_id"] == str(test_session_completed.job_posting_id)

    # Verify in database
    result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == data["id"]))
    new_session = result.scalar_one_or_none()

    assert new_session is not None
    assert new_session.retake_number == 2
    assert new_session.original_session_id == test_session_completed.id
    assert new_session.status == "active"


@pytest.mark.asyncio
async def test_create_retake_success_second_retake(
    async_client: AsyncClient, auth_headers: dict, test_session_completed, db_session
):
    """Test creating second retake - should chain to original."""
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    # Create first retake
    first_retake_response = await async_client.post(
        f"/api/v1/sessions/{test_session_completed.id}/retake",
        headers=auth_headers,
    )
    assert first_retake_response.status_code == 201
    first_retake_id = first_retake_response.json()["id"]

    # Mark first retake as completed
    result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == first_retake_id))
    first_retake = result.scalar_one()
    first_retake.status = "completed"
    await db_session.commit()

    # Create second retake from first retake
    second_retake_response = await async_client.post(
        f"/api/v1/sessions/{first_retake_id}/retake",
        headers=auth_headers,
    )

    assert second_retake_response.status_code == 201
    data = second_retake_response.json()

    # Should increment to 3 and still point to original session
    assert data["retake_number"] == 3
    assert data["original_session_id"] == str(test_session_completed.id)
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_create_retake_chain_integrity(
    async_client: AsyncClient, auth_headers: dict, test_session_completed, db_session
):
    """Test that retake chain maintains integrity across multiple retakes."""
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    original_id = test_session_completed.id

    # Create 3 retakes in sequence
    previous_id = original_id
    for expected_retake_num in [2, 3, 4]:
        # Create retake
        response = await async_client.post(
            f"/api/v1/sessions/{previous_id}/retake",
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()

        # Verify retake fields
        assert data["retake_number"] == expected_retake_num
        assert data["original_session_id"] == str(original_id)

        # Mark as completed for next iteration
        result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == data["id"]))
        retake = result.scalar_one()
        retake.status = "completed"
        await db_session.commit()

        previous_id = data["id"]


@pytest.mark.asyncio
async def test_create_retake_not_completed_returns_400(async_client: AsyncClient, auth_headers: dict, test_session):
    """Test error when retaking non-completed session."""
    # test_session has status='active'
    response = await async_client.post(
        f"/api/v1/sessions/{test_session.id}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_COMPLETED"
    assert "must be completed" in data["detail"]["message"].lower()


@pytest.mark.asyncio
async def test_create_retake_nonexistent_session_returns_404(async_client: AsyncClient, auth_headers: dict):
    """Test error when retaking non-existent session."""
    fake_id = str(uuid.uuid4())
    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_retake_other_users_session_returns_403(
    async_client: AsyncClient, auth_headers: dict, other_user_completed_session
):
    """Test error when retaking another user's session."""
    response = await async_client.post(
        f"/api/v1/sessions/{other_user_completed_session['id']}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_create_retake_unauthenticated_returns_401(async_client: AsyncClient, test_session_completed):
    """Test error when retaking without authentication."""
    response = await async_client.post(
        f"/api/v1/sessions/{test_session_completed.id}/retake",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_retake_missing_job_posting_returns_400(
    async_client: AsyncClient, auth_headers: dict, test_user, db_session
):
    """Test error when retaking session with deleted job posting."""
    from app.models.interview_session import InterviewSession

    # Create session without job posting
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=None,
        status="completed",
        current_question_number=5,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    response = await async_client.post(
        f"/api/v1/sessions/{session.id}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "MISSING_JOB_POSTING"


@pytest.mark.asyncio
async def test_create_retake_persists_to_database(
    async_client: AsyncClient, auth_headers: dict, test_session_completed, db_session
):
    """Test that retake session is properly persisted to database."""
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    response = await async_client.post(
        f"/api/v1/sessions/{test_session_completed.id}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 201
    new_session_id = response.json()["id"]

    # Verify in database
    result = await db_session.execute(select(InterviewSession).where(InterviewSession.id == new_session_id))
    new_session = result.scalar_one_or_none()

    assert new_session is not None
    assert new_session.user_id == test_session_completed.user_id
    assert new_session.job_posting_id == test_session_completed.job_posting_id
    assert new_session.status == "active"
    assert new_session.current_question_number == 0
    assert new_session.retake_number == test_session_completed.retake_number + 1


@pytest.mark.asyncio
async def test_create_retake_response_includes_all_fields(
    async_client: AsyncClient, auth_headers: dict, test_session_completed
):
    """Test that retake response includes all required session fields."""
    response = await async_client.post(
        f"/api/v1/sessions/{test_session_completed.id}/retake",
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()

    # Verify all SessionResponse fields are present
    required_fields = [
        "id",
        "user_id",
        "job_posting_id",
        "status",
        "current_question_number",
        "retake_number",
        "original_session_id",
        "created_at",
        "updated_at",
    ]

    for field in required_fields:
        assert field in data, f"Missing field: {field}"
