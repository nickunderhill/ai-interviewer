"""
Tests for feedback analysis service.
"""

import json
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi import HTTPException
import pytest

from app.models.interview_session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.resume import Resume
from app.models.session_message import SessionMessage
from app.services import feedback_analysis_service


@pytest.fixture
def mock_openai_response():
    """Valid OpenAI API response JSON."""
    return json.dumps(
        {
            "technical_accuracy_score": 85,
            "communication_clarity_score": 78,
            "problem_solving_score": 92,
            "relevance_score": 80,
            "technical_feedback": "Strong grasp of core concepts with minor gaps in advanced topics.",
            "communication_feedback": "Clear explanations, could improve structure in complex responses.",
            "problem_solving_feedback": "Excellent analytical approach and systematic problem decomposition.",
            "relevance_feedback": "Good alignment with job requirements, relevant experience demonstrated.",
            "overall_comments": "Strong candidate with solid fundamentals and good problem-solving skills.",
            "knowledge_gaps": [
                "Advanced concurrency patterns",
                "Distributed systems design",
            ],
            "learning_recommendations": [
                "Study distributed systems textbook",
                "Practice LeetCode hard problems",
                "Review concurrency primitives in depth",
            ],
        }
    )


@pytest.fixture
async def complete_interview_session(db_session, test_user):
    """Create a complete interview session with all required data."""
    # Create resume
    resume = Resume(
        user_id=test_user.id,
        content="Software Engineer with 5 years of Python and FastAPI experience.",
    )
    db_session.add(resume)

    # Create job posting
    job_posting = JobPosting(
        user_id=test_user.id,
        title="Senior Backend Engineer",
        company="Tech Corp",
        description="Build scalable APIs with Python and FastAPI",
        experience_level="Senior",
        tech_stack=["Python", "FastAPI", "PostgreSQL"],
    )
    db_session.add(job_posting)
    await db_session.flush()

    # Create session
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=job_posting.id,
        status="completed",
    )
    db_session.add(session)
    await db_session.flush()

    # Add Q&A messages
    messages = [
        SessionMessage(
            session_id=session.id,
            message_type="question",
            content="What is your experience with async Python?",
        ),
        SessionMessage(
            session_id=session.id,
            message_type="answer",
            content="I have extensive experience with asyncio and async/await patterns.",
        ),
        SessionMessage(
            session_id=session.id,
            message_type="question",
            content="How would you design a rate limiter?",
        ),
        SessionMessage(
            session_id=session.id,
            message_type="answer",
            content="I would use a token bucket algorithm with Redis for distributed rate limiting.",
        ),
    ]
    for msg in messages:
        db_session.add(msg)

    await db_session.commit()
    await db_session.refresh(session)
    return session


@pytest.mark.asyncio
async def test_analyze_session_success(db_session, test_user, complete_interview_session, mock_openai_response):
    """Test successful feedback analysis with valid OpenAI response."""
    with patch("app.services.feedback_analysis_service.OpenAIService") as mock_openai:
        mock_service = MagicMock()
        mock_service.generate_chat_completion.return_value = mock_openai_response
        mock_openai.return_value = mock_service

        result = await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=complete_interview_session.id,
            current_user=test_user,
        )

        assert result.technical_accuracy_score == 85
        assert result.communication_clarity_score == 78
        assert result.problem_solving_score == 92
        assert result.relevance_score == 80
        assert "Strong grasp" in result.technical_feedback
        assert len(result.knowledge_gaps) == 2
        assert len(result.learning_recommendations) == 3
        assert result.overall_comments == "Strong candidate with solid fundamentals and good problem-solving skills."


@pytest.mark.asyncio
async def test_analyze_session_not_found(db_session, test_user):
    """Test error when session does not exist."""
    with pytest.raises(HTTPException) as exc_info:
        await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=uuid4(),
            current_user=test_user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["code"] == "SESSION_NOT_FOUND"


@pytest.mark.asyncio
async def test_analyze_session_missing_resume(db_session, test_user, complete_interview_session):
    """Test error when user has no resume."""
    # Delete resume using SQLAlchemy delete
    from sqlalchemy import delete

    from app.models.resume import Resume

    stmt = delete(Resume).where(Resume.user_id == test_user.id)
    await db_session.execute(stmt)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=complete_interview_session.id,
            current_user=test_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "RESUME_REQUIRED"


@pytest.mark.asyncio
async def test_analyze_session_missing_job_posting(db_session, test_user):
    """Test error when session has no job posting."""
    # Create session without job posting
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=None,
        status="completed",
    )
    db_session.add(session)
    await db_session.commit()

    # Create resume
    resume = Resume(
        user_id=test_user.id,
        content="Test resume content",
    )
    db_session.add(resume)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=session.id,
            current_user=test_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "JOB_POSTING_REQUIRED"


@pytest.mark.asyncio
async def test_analyze_session_no_answers(db_session, test_user):
    """Test error when session has no Q&A pairs."""
    # Create minimal session without messages
    resume = Resume(
        user_id=test_user.id,
        content="Test resume",
    )
    db_session.add(resume)

    job_posting = JobPosting(
        user_id=test_user.id,
        title="Test Job",
        description="Test description",
    )
    db_session.add(job_posting)
    await db_session.flush()

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=job_posting.id,
        status="completed",
    )
    db_session.add(session)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=session.id,
            current_user=test_user,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["code"] == "NO_ANSWERS"


@pytest.mark.asyncio
async def test_analyze_session_malformed_json(db_session, test_user, complete_interview_session):
    """Test error when OpenAI returns malformed JSON."""
    with patch("app.services.feedback_analysis_service.OpenAIService") as mock_openai:
        mock_service = MagicMock()
        mock_service.generate_chat_completion.return_value = "This is not JSON"
        mock_openai.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await feedback_analysis_service.analyze_session(
                db=db_session,
                session_id=complete_interview_session.id,
                current_user=test_user,
            )

        assert exc_info.value.status_code == 502
        assert exc_info.value.detail["code"] == "FEEDBACK_PARSE_FAILED"


@pytest.mark.asyncio
async def test_analyze_session_invalid_schema(db_session, test_user, complete_interview_session):
    """Test error when OpenAI returns JSON with invalid schema."""
    invalid_response = json.dumps(
        {
            "technical_accuracy_score": "not_a_number",  # Invalid type
            "missing_required_fields": True,
        }
    )

    with patch("app.services.feedback_analysis_service.OpenAIService") as mock_openai:
        mock_service = MagicMock()
        mock_service.generate_chat_completion.return_value = invalid_response
        mock_openai.return_value = mock_service

        with pytest.raises(HTTPException) as exc_info:
            await feedback_analysis_service.analyze_session(
                db=db_session,
                session_id=complete_interview_session.id,
                current_user=test_user,
            )

        assert exc_info.value.status_code == 502
        assert exc_info.value.detail["code"] == "FEEDBACK_PARSE_FAILED"


@pytest.mark.asyncio
async def test_analyze_session_score_clamping(db_session, test_user, complete_interview_session):
    """Test that out-of-range scores are clamped to 0-100."""
    response_with_invalid_scores = json.dumps(
        {
            "technical_accuracy_score": 150,  # Over 100
            "communication_clarity_score": -10,  # Below 0
            "problem_solving_score": 50,
            "relevance_score": 200,  # Over 100
            "technical_feedback": "Test",
            "communication_feedback": "Test",
            "problem_solving_feedback": "Test",
            "relevance_feedback": "Test",
            "overall_comments": None,
            "knowledge_gaps": [],
            "learning_recommendations": [],
        }
    )

    with patch("app.services.feedback_analysis_service.OpenAIService") as mock_openai:
        mock_service = MagicMock()
        mock_service.generate_chat_completion.return_value = response_with_invalid_scores
        mock_openai.return_value = mock_service

        result = await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=complete_interview_session.id,
            current_user=test_user,
        )

        # Verify scores are clamped
        assert result.technical_accuracy_score == 100
        assert result.communication_clarity_score == 0
        assert result.problem_solving_score == 50
        assert result.relevance_score == 100


@pytest.mark.asyncio
async def test_build_analysis_prompt_format(db_session, test_user, complete_interview_session):
    """Test that the prompt includes all required information."""
    with patch("app.services.feedback_analysis_service.OpenAIService") as mock_openai:
        mock_service = MagicMock()
        mock_service.generate_chat_completion.return_value = json.dumps(
            {
                "technical_accuracy_score": 75,
                "communication_clarity_score": 75,
                "problem_solving_score": 75,
                "relevance_score": 75,
                "technical_feedback": "Test",
                "communication_feedback": "Test",
                "problem_solving_feedback": "Test",
                "relevance_feedback": "Test",
                "overall_comments": "Test",
                "knowledge_gaps": [],
                "learning_recommendations": [],
            }
        )
        mock_openai.return_value = mock_service

        await feedback_analysis_service.analyze_session(
            db=db_session,
            session_id=complete_interview_session.id,
            current_user=test_user,
        )

        # Verify the prompt was called with correct format
        call_args = mock_service.generate_chat_completion.call_args
        prompt = call_args[1]["messages"][0]["content"]

        # Verify prompt contains all required sections
        assert "JOB POSTING:" in prompt
        assert "Senior Backend Engineer" in prompt
        assert "CANDIDATE'S RESUME:" in prompt
        assert "Software Engineer with 5 years" in prompt
        assert "INTERVIEW TRANSCRIPT:" in prompt
        assert "Q1:" in prompt
        assert "A1:" in prompt
        assert "async Python" in prompt
        assert "Python, FastAPI, PostgreSQL" in prompt
