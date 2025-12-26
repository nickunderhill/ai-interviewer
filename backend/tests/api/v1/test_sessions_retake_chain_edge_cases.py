"""
Test for retake chain endpoint edge cases.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_retake_chain_with_sessions_without_feedback(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session_completed,
    db_session,
):
    """Test retake chain includes sessions even if they don't have feedback."""
    from app.models.interview_session import InterviewSession

    # Create a retake without feedback
    retake_no_feedback = InterviewSession(
        user_id=test_session_completed.user_id,
        job_posting_id=test_session_completed.job_posting_id,
        status="completed",
        retake_number=2,
        original_session_id=test_session_completed.id,
    )
    db_session.add(retake_no_feedback)
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/sessions/{test_session_completed.id}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    # First session may have feedback, second doesn't
    assert data[0]["retake_number"] == 1
    assert data[1]["retake_number"] == 2
    assert data[1]["feedback"] is None  # No feedback for this session
