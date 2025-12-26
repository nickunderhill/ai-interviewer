"""Tests for question generation background tasks."""

from unittest.mock import patch
from uuid import uuid4

from fastapi import HTTPException
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_session import InterviewSession
from app.models.operation import Operation
from app.models.session_message import SessionMessage
from app.tasks.question_tasks import generate_question_task


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_creates_message(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """Test task creates SessionMessage after generating question."""
    # Configure mock to use the test's db_session
    mock_session_local.return_value.__aenter__.return_value = db_session

    mock_generate.return_value = {
        "question_text": "What is your experience with Python?",
        "question_type": "technical",
    }

    # Create session with job posting and user
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Create operation
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    initial_question_number = session.current_question_number

    # Run task
    await generate_question_task(operation.id, session.id)

    # Verify message created
    result = await db_session.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == session.id,
            SessionMessage.message_type == "question",
        )
    )
    message = result.scalar_one_or_none()

    assert message is not None
    assert message.content == "What is your experience with Python?"
    assert message.question_type == "technical"
    assert message.session_id == session.id

    # Verify session updated
    await db_session.refresh(session)
    assert session.current_question_number == initial_question_number + 1


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_updates_operation(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """Test task updates operation with completed status and result."""
    mock_session_local.return_value.__aenter__.return_value = db_session

    mock_generate.return_value = {
        "question_text": "Test question",
        "question_type": "behavioral",
    }

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    await generate_question_task(operation.id, session.id)

    # Verify operation completed
    await db_session.refresh(operation)
    assert operation.status == "completed"
    assert operation.result["question_text"] == "Test question"
    assert operation.result["question_type"] == "behavioral"


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_handles_generation_failure(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """Test task handles generation failure gracefully."""
    mock_session_local.return_value.__aenter__.return_value = db_session
    mock_generate.side_effect = Exception("OpenAI error")

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    await generate_question_task(operation.id, session.id)

    # Verify operation failed
    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert operation.error_message is not None
    assert "What to do:" in operation.error_message


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_rolls_back_partial_state_on_db_failure(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """If DB write fails, task must rollback and not persist partial state."""
    mock_session_local.return_value.__aenter__.return_value = db_session
    mock_generate.return_value = {
        "question_text": "What is Python?",
        "question_type": "technical",
    }

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Simulate a DB failure during the atomic write (after objects are staged).
    with patch.object(db_session, "flush", side_effect=Exception("db flush failed")):
        await generate_question_task(operation.id, session.id)

    await db_session.refresh(operation)
    assert operation.status == "failed"

    await db_session.refresh(session)
    assert session.current_question_number == 0

    result = await db_session.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == session.id,
            SessionMessage.message_type == "question",
        )
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_masks_sensitive_error_message_from_http_exception(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """Ensure error_message stored on Operation is safe (no API keys)."""
    mock_session_local.return_value.__aenter__.return_value = db_session
    mock_generate.side_effect = HTTPException(
        status_code=502,
        detail={
            "code": "OPENAI_INVALID_RESPONSE",
            "message": "OpenAI failed with key sk-1234567890abcdef",
        },
    )

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    await generate_question_task(operation.id, session.id)

    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert "sk-" not in (operation.error_message or "")
    assert "unexpected response" in (operation.error_message or "").lower()
    assert "What to do:" in (operation.error_message or "")


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_sets_user_friendly_message_for_invalid_api_key(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """AI auth failures should store actionable, non-technical messages."""

    mock_session_local.return_value.__aenter__.return_value = db_session
    mock_generate.side_effect = HTTPException(
        status_code=400,
        detail={
            "code": "INVALID_API_KEY",
            "message": "Invalid OpenAI API key sk-1234567890abcdef",
        },
    )

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    await generate_question_task(operation.id, session.id)

    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert operation.error_message is not None
    assert "OpenAI API key" in operation.error_message
    assert "What to do:" in operation.error_message
    assert "sk-" not in operation.error_message


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_multiple_questions_create_separate_messages(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """Test multiple question generations create separate message records."""
    mock_session_local.return_value.__aenter__.return_value = db_session

    mock_generate.side_effect = [
        {"question_text": "First question", "question_type": "technical"},
        {"question_text": "Second question", "question_type": "behavioral"},
    ]

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    # Generate first question
    operation1 = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation1)
    await db_session.commit()
    await db_session.refresh(operation1)

    await generate_question_task(operation1.id, session.id)

    # Generate second question
    operation2 = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation2)
    await db_session.commit()
    await db_session.refresh(operation2)

    await generate_question_task(operation2.id, session.id)

    # Verify two messages created
    result = await db_session.execute(
        select(SessionMessage)
        .where(
            SessionMessage.session_id == session.id,
            SessionMessage.message_type == "question",
        )
        .order_by(SessionMessage.created_at)
    )
    messages = result.scalars().all()

    assert len(messages) == 2
    assert messages[0].content == "First question"
    assert messages[1].content == "Second question"

    # Verify session question number incremented twice
    await db_session.refresh(session)
    assert session.current_question_number == 2  # Started at 0, incremented twice


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
async def test_question_task_handles_nonexistent_session(
    mock_session_local, db_session: AsyncSession
):
    """Test task handles non-existent session gracefully."""
    mock_session_local.return_value.__aenter__.return_value = db_session

    fake_session_id = uuid4()

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    await generate_question_task(operation.id, fake_session_id)

    # Verify operation failed
    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert operation.error_message is not None
    assert "what to do:" in operation.error_message.lower()
    assert "session could not be found" in operation.error_message.lower()


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_question_task_all_fields_populated(
    mock_generate,
    mock_session_local,
    db_session: AsyncSession,
    test_user,
    test_job_posting,
):
    """Test that SessionMessage has all required fields populated."""
    mock_session_local.return_value.__aenter__.return_value = db_session

    mock_generate.return_value = {
        "question_text": "Describe your leadership experience",
        "question_type": "situational",
    }

    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=0,
    )
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)

    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    await generate_question_task(operation.id, session.id)

    # Get the created message
    result = await db_session.execute(
        select(SessionMessage).where(SessionMessage.session_id == session.id)
    )
    message = result.scalar_one()

    # Verify all fields
    assert message.id is not None
    assert message.session_id == session.id
    assert message.message_type == "question"
    assert message.content == "Describe your leadership experience"
    assert message.question_type == "situational"
    assert message.created_at is not None
