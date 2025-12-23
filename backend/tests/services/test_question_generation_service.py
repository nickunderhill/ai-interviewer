"""Tests for question generation service."""

import pytest
from unittest.mock import Mock, patch

from app.services.question_generation_service import (
    build_question_prompt,
    generate_question,
    get_question_type_for_round,
)
from app.models.interview_session import InterviewSession


def test_question_type_rotation():
    """Test question type rotation logic."""
    assert get_question_type_for_round(1) == "technical"
    assert get_question_type_for_round(2) == "behavioral"
    assert get_question_type_for_round(3) == "situational"
    assert get_question_type_for_round(4) == "technical"
    assert get_question_type_for_round(5) == "behavioral"
    assert get_question_type_for_round(6) == "situational"
    assert get_question_type_for_round(7) == "technical"


def test_question_type_rotation_edge_cases():
    """Test question type rotation with edge cases."""
    assert get_question_type_for_round(0) == "technical"
    assert get_question_type_for_round(100) == "technical"
    assert get_question_type_for_round(101) == "behavioral"


def test_build_question_prompt_with_full_context():
    """Test prompt includes all job and resume context."""
    prompt = build_question_prompt(
        job_title="Senior Python Developer",
        job_company="TechCorp",
        job_description="Build scalable APIs",
        tech_stack="Python, FastAPI, PostgreSQL",
        experience_level="Senior",
        resume_content="5 years Python experience...",
        question_type="technical",
    )

    assert "Senior Python Developer" in prompt
    assert "TechCorp" in prompt
    assert "Build scalable APIs" in prompt
    assert "Python, FastAPI, PostgreSQL" in prompt
    assert "Senior" in prompt
    assert "5 years Python experience" in prompt
    assert "technical" in prompt.lower()


def test_build_question_prompt_without_resume():
    """Test prompt handles missing resume."""
    prompt = build_question_prompt(
        job_title="Developer",
        job_company=None,
        job_description="Build apps",
        tech_stack=None,
        experience_level=None,
        resume_content=None,
        question_type="behavioral",
    )

    assert "Developer" in prompt
    assert "Build apps" in prompt
    assert "No resume provided" in prompt
    assert "behavioral" in prompt.lower()


def test_build_question_prompt_behavioral_type():
    """Test behavioral question prompt includes STAR instructions."""
    prompt = build_question_prompt(
        job_title="Product Manager",
        job_company="StartupCo",
        job_description="Lead product development",
        tech_stack=None,
        experience_level="Mid",
        resume_content="Led teams of 5",
        question_type="behavioral",
    )

    assert "behavioral" in prompt.lower()
    assert "STAR" in prompt
    assert "past experiences" in prompt.lower()
    assert "Led teams of 5" in prompt


def test_build_question_prompt_situational_type():
    """Test situational question prompt includes scenario instructions."""
    prompt = build_question_prompt(
        job_title="Engineering Manager",
        job_company="BigTech",
        job_description="Manage engineering teams",
        tech_stack="Cloud, Microservices",
        experience_level="Senior",
        resume_content="Managed 10+ engineers",
        question_type="situational",
    )

    assert "situational" in prompt.lower()
    assert "hypothetical scenario" in prompt.lower()
    assert "Managed 10+ engineers" in prompt
    assert "Cloud, Microservices" in prompt


@pytest.mark.asyncio
@patch("app.services.question_generation_service.OpenAIService")
async def test_generate_question_success_with_resume(
    mock_openai_service,
):
    """Test successful question generation with full context."""
    # Mock session with relationships
    mock_session = Mock(spec=InterviewSession)
    mock_session.id = "test-session-id"
    mock_session.current_question_number = 0

    mock_job = Mock()
    mock_job.title = "Developer"
    mock_job.company = "TestCorp"
    mock_job.description = "Build software"
    mock_job.tech_stack = "Python"
    mock_job.experience_level = "Mid"
    mock_session.job_posting = mock_job

    mock_user = Mock()
    mock_resume = Mock()
    mock_resume.content = "Resume content with Python experience"
    mock_user.resume = mock_resume
    mock_session.user = mock_user

    # Mock OpenAI response
    mock_service_instance = Mock()
    mock_service_instance.generate_chat_completion.return_value = (
        "What is your experience with Python?"
    )
    mock_openai_service.return_value = mock_service_instance

    result = await generate_question(mock_session)

    assert result["question_text"] == "What is your experience with Python?"
    assert result["question_type"] == "technical"

    # Verify OpenAI service was called correctly
    mock_openai_service.assert_called_once_with(mock_user)
    mock_service_instance.generate_chat_completion.assert_called_once()
    call_args = mock_service_instance.generate_chat_completion.call_args
    assert call_args[1]["model"] == "gpt-3.5-turbo"
    assert call_args[1]["temperature"] == 0.7
    assert call_args[1]["max_tokens"] == 200


@pytest.mark.asyncio
@patch("app.services.question_generation_service.OpenAIService")
async def test_generate_question_without_resume(mock_openai_service):
    """Test question generation when user has no resume."""
    mock_session = Mock(spec=InterviewSession)
    mock_session.id = "test-session-id"
    mock_session.current_question_number = 1

    mock_job = Mock()
    mock_job.title = "Backend Engineer"
    mock_job.company = "StartupCo"
    mock_job.description = "Build APIs"
    mock_job.tech_stack = "FastAPI, PostgreSQL"
    mock_job.experience_level = "Junior"
    mock_session.job_posting = mock_job

    mock_user = Mock()
    mock_user.resume = None  # No resume
    mock_session.user = mock_user

    mock_service_instance = Mock()
    mock_service_instance.generate_chat_completion.return_value = (
        "Tell me about a time you worked in a team"
    )
    mock_openai_service.return_value = mock_service_instance

    result = await generate_question(mock_session)

    assert result["question_text"] == "Tell me about a time you worked in a team"
    assert result["question_type"] == "behavioral"

    # Verify prompt was still generated
    call_args = mock_service_instance.generate_chat_completion.call_args
    prompt = call_args[1]["messages"][0]["content"]
    assert "No resume provided" in prompt


@pytest.mark.asyncio
async def test_generate_question_missing_job_posting():
    """Test error when session missing job_posting."""
    mock_session = Mock(spec=InterviewSession)
    mock_session.id = "test-session-id"
    mock_session.job_posting = None

    with pytest.raises(ValueError, match="job_posting loaded"):
        await generate_question(mock_session)


@pytest.mark.asyncio
@patch("app.services.question_generation_service.OpenAIService")
async def test_generate_question_cycles_through_types(
    mock_openai_service,
):
    """Test question type cycles correctly through multiple generations."""
    # Create base mocks
    mock_job = Mock()
    mock_job.title = "Developer"
    mock_job.company = "TestCorp"
    mock_job.description = "Build software"
    mock_job.tech_stack = "Python"
    mock_job.experience_level = "Mid"

    mock_user = Mock()
    mock_user.resume = None

    mock_service_instance = Mock()
    mock_service_instance.generate_chat_completion.return_value = "Test question"
    mock_openai_service.return_value = mock_service_instance

    # Test questions 1-6 to verify full cycle
    expected_types = [
        "technical",
        "behavioral",
        "situational",
        "technical",
        "behavioral",
        "situational",
    ]

    for i, expected_type in enumerate(expected_types):
        mock_session = Mock(spec=InterviewSession)
        mock_session.id = f"session-{i}"
        mock_session.current_question_number = i
        mock_session.job_posting = mock_job
        mock_session.user = mock_user

        result = await generate_question(mock_session)
        assert result["question_type"] == expected_type


@pytest.mark.asyncio
@patch("app.services.question_generation_service.OpenAIService")
async def test_generate_question_cleans_response(mock_openai_service):
    """Test that generated question text is cleaned up."""
    mock_session = Mock(spec=InterviewSession)
    mock_session.id = "test-session-id"
    mock_session.current_question_number = 0

    mock_job = Mock()
    mock_job.title = "Developer"
    mock_job.company = "TestCorp"
    mock_job.description = "Build software"
    mock_job.tech_stack = "Python"
    mock_job.experience_level = "Mid"
    mock_session.job_posting = mock_job

    mock_user = Mock()
    mock_user.resume = None
    mock_session.user = mock_user

    # Mock response with quotes and whitespace
    mock_service_instance = Mock()
    mock_service_instance.generate_chat_completion.return_value = (
        '  "What is your experience?"  '
    )
    mock_openai_service.return_value = mock_service_instance

    result = await generate_question(mock_session)

    # Verify quotes and whitespace removed
    assert result["question_text"] == "What is your experience?"


@pytest.mark.asyncio
@patch("app.services.question_generation_service.OpenAIService")
async def test_generate_question_openai_failure(mock_openai_service):
    """Test error handling when OpenAI service fails."""
    mock_session = Mock(spec=InterviewSession)
    mock_session.id = "test-session-id"
    mock_session.current_question_number = 0

    mock_job = Mock()
    mock_job.title = "Developer"
    mock_job.company = "TestCorp"
    mock_job.description = "Build software"
    mock_job.tech_stack = "Python"
    mock_job.experience_level = "Mid"
    mock_session.job_posting = mock_job

    mock_user = Mock()
    mock_user.resume = None
    mock_session.user = mock_user

    # Mock OpenAI service to raise exception
    mock_service_instance = Mock()
    mock_service_instance.generate_chat_completion.side_effect = Exception(
        "OpenAI API error"
    )
    mock_openai_service.return_value = mock_service_instance

    with pytest.raises(Exception, match="OpenAI API error"):
        await generate_question(mock_session)
