"""
Test that retake chain endpoint returns dimension scores for story 7-5.
"""

from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_retake_chain_includes_dimension_scores(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session_with_feedback,
):
    """Test that retake chain includes all 4 dimension scores."""
    response = await async_client.get(
        f"/api/v1/sessions/{test_completed_session_with_feedback['id']}/retake-chain",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    session_data = data[0]

    # Verify feedback exists
    assert "feedback" in session_data
    feedback = session_data["feedback"]
    assert feedback is not None

    # Verify all 4 dimension scores are present
    assert "technical_accuracy_score" in feedback
    assert "communication_clarity_score" in feedback
    assert "problem_solving_score" in feedback
    assert "relevance_score" in feedback

    # Verify scores are valid
    for score_key in [
        "technical_accuracy_score",
        "communication_clarity_score",
        "problem_solving_score",
        "relevance_score",
    ]:
        score = feedback[score_key]
        assert isinstance(score, int)
        assert 0 <= score <= 100, f"{score_key} should be between 0-100"
