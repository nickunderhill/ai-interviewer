"""
Tests for GET /api/v1/sessions/{id}/retake-chain endpoint.
"""

import uuid

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_get_retake_chain_single_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_completed,
):
    """Test getting retake chain for a single session (no retakes)."""
    response = await async_client.get(
        f"/api/v1/sessions/{test_session_completed.id}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(test_session_completed.id)
    assert data[0]["retake_number"] == 1


@pytest.mark.asyncio
async def test_get_retake_chain_with_retakes(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_completed,
    db_session,
):
    """Test getting retake chain with multiple retakes."""
    from app.models.interview_session import InterviewSession

    # Create two retakes
    retake1 = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="completed",
        retake_number=2,
        original_session_id=test_session_completed.id,
    )
    retake2 = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="active",
        retake_number=3,
        original_session_id=test_session_completed.id,
    )
    db_session.add(retake1)
    db_session.add(retake2)
    await db_session.commit()

    # Get chain from original session
    response = await async_client.get(
        f"/api/v1/sessions/{test_session_completed.id}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 3
    assert data[0]["retake_number"] == 1
    assert data[1]["retake_number"] == 2
    assert data[2]["retake_number"] == 3
    # Verify all point to same original
    assert data[1]["original_session_id"] == str(test_session_completed.id)
    assert data[2]["original_session_id"] == str(test_session_completed.id)


@pytest.mark.asyncio
async def test_get_retake_chain_from_retake_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_completed,
    db_session,
):
    """Test getting chain when querying from a retake (not original)."""
    from app.models.interview_session import InterviewSession

    # Create a retake
    retake = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="completed",
        retake_number=2,
        original_session_id=test_session_completed.id,
    )
    db_session.add(retake)
    await db_session.commit()
    await db_session.refresh(retake)

    # Query from the retake, should still get full chain
    response = await async_client.get(
        f"/api/v1/sessions/{retake.id}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["id"] == str(test_session_completed.id)  # Original comes first
    assert data[1]["id"] == str(retake.id)


@pytest.mark.asyncio
async def test_get_retake_chain_includes_feedback(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session_with_feedback,
):
    """Test that retake chain includes feedback data."""
    response = await async_client.get(
        f"/api/v1/sessions/{test_completed_session_with_feedback['id']}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    session_data = data[0]

    # Verify feedback is included
    assert "feedback" in session_data
    assert session_data["feedback"] is not None
    assert "overall_score" in session_data["feedback"]
    assert "technical_accuracy_score" in session_data["feedback"]


@pytest.mark.asyncio
async def test_get_retake_chain_nonexistent_session_returns_404(
    async_client: AsyncClient, auth_headers: dict
):
    """Test error when getting chain for non-existent session."""
    fake_id = str(uuid.uuid4())
    response = await async_client.get(
        f"/api/v1/sessions/{fake_id}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_retake_chain_other_users_session_returns_403(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_completed_session,
):
    """Test error when getting chain for another user's session."""
    response = await async_client.get(
        f"/api/v1/sessions/{other_user_completed_session['id']}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_retake_chain_unauthenticated_returns_401(
    async_client: AsyncClient, test_session_completed
):
    """Test error when getting chain without authentication."""
    response = await async_client.get(
        f"/api/v1/sessions/{test_session_completed.id}/retake-chain",
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_retake_chain_ordered_by_retake_number(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_completed,
    db_session,
):
    """Test that sessions are returned in correct order."""
    from app.models.interview_session import InterviewSession

    # Create retakes in non-sequential order
    retake3 = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="active",
        retake_number=4,
        original_session_id=test_session_completed.id,
    )
    retake1 = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="completed",
        retake_number=2,
        original_session_id=test_session_completed.id,
    )
    retake2 = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="completed",
        retake_number=3,
        original_session_id=test_session_completed.id,
    )
    # Add in scrambled order
    db_session.add(retake3)
    db_session.add(retake1)
    db_session.add(retake2)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/sessions/{test_session_completed.id}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Should be ordered 1, 2, 3, 4
    assert len(data) == 4
    assert [s["retake_number"] for s in data] == [1, 2, 3, 4]
