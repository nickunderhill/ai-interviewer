"""Tests for feedback generation background tasks."""

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_feedback import InterviewFeedback
from app.models.operation import Operation
from app.schemas.feedback import FeedbackAnalysisResult
from app.tasks.feedback_tasks import generate_feedback_task


@pytest.mark.asyncio
@patch("app.tasks.feedback_tasks.get_db_context")
@patch("app.tasks.feedback_tasks.feedback_analysis_service.analyze_session")
async def test_feedback_task_rolls_back_and_marks_failed_on_integrity_error(
    mock_analyze_session,
    mock_db_context,
    db_session: AsyncSession,
    test_user,
):
    """If feedback insert hits IntegrityError, operation is failed and no partial writes persist."""

    @asynccontextmanager
    async def _ctx():
        yield db_session

    mock_db_context.return_value = _ctx()

    mock_analyze_session.return_value = FeedbackAnalysisResult(
        technical_accuracy_score=80,
        communication_clarity_score=70,
        problem_solving_score=90,
        relevance_score=60,
        technical_feedback="t",
        communication_feedback="c",
        problem_solving_feedback="p",
        relevance_feedback="r",
        overall_comments=None,
        knowledge_gaps=["g1"],
        learning_recommendations=["l1"],
    )

    operation = Operation(operation_type="feedback_analysis", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Simulate unique constraint / duplicate insert.
    integrity_error = IntegrityError("stmt", "params", Exception("duplicate"))
    with patch.object(db_session, "flush", side_effect=integrity_error):
        await generate_feedback_task(
            operation_id=operation.id,
            session_id=operation.id,  # not used when analyze_session is mocked
            user_id=test_user.id,
        )

    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert "feedback" in (operation.error_message or "").lower()

    result = await db_session.execute(select(InterviewFeedback))
    assert result.scalars().first() is None
