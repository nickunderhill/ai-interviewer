"""Tests for Operation model."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation import Operation


@pytest.mark.asyncio
async def test_create_operation(db_session: AsyncSession):
    """Test basic operation creation."""
    operation = Operation(
        operation_type="question_generation",
        status="pending",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.id is not None
    assert operation.operation_type == "question_generation"
    assert operation.status == "pending"
    assert operation.result is None
    assert operation.error_message is None
    assert operation.created_at is not None
    assert operation.updated_at is not None


@pytest.mark.asyncio
async def test_operation_json_result(db_session: AsyncSession):
    """Test storing JSON result in JSONB column."""
    test_result = {
        "question": "What is Python?",
        "question_type": "technical",
        "metadata": {"difficulty": "medium"},
    }

    operation = Operation(
        operation_type="question_generation",
        status="completed",
        result=test_result,
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.result is not None
    assert operation.result["question"] == "What is Python?"
    assert operation.result["question_type"] == "technical"
    assert operation.result["metadata"]["difficulty"] == "medium"


@pytest.mark.asyncio
async def test_operation_error_handling(db_session: AsyncSession):
    """Test storing error messages for failed operations."""
    operation = Operation(
        operation_type="question_generation",
        status="failed",
        error_message="OpenAI API rate limit exceeded",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.status == "failed"
    assert operation.error_message == "OpenAI API rate limit exceeded"
    assert operation.result is None


@pytest.mark.asyncio
async def test_operation_timestamps_utc(db_session: AsyncSession):
    """Test timestamps are UTC-aware."""
    operation = Operation(
        operation_type="question_generation",
        status="pending",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.created_at.tzinfo is not None
    assert operation.updated_at.tzinfo is not None


@pytest.mark.asyncio
async def test_operation_status_transitions(db_session: AsyncSession):
    """Test operation status can transition through states."""
    operation = Operation(
        operation_type="question_generation",
        status="pending",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Transition to processing
    operation.status = "processing"
    await db_session.commit()
    await db_session.refresh(operation)
    assert operation.status == "processing"

    # Transition to completed
    operation.status = "completed"
    operation.result = {"question": "Test question"}
    await db_session.commit()
    await db_session.refresh(operation)
    assert operation.status == "completed"
    assert operation.result is not None


@pytest.mark.asyncio
async def test_operation_type_feedback_analysis(db_session: AsyncSession):
    """Test operation with feedback_analysis type."""
    operation = Operation(
        operation_type="feedback_analysis",
        status="completed",
        result={
            "overall_score": 85,
            "dimension_scores": {"technical": 90, "communication": 80},
        },
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.operation_type == "feedback_analysis"
    assert operation.result["overall_score"] == 85


@pytest.mark.asyncio
async def test_operation_nullable_fields(db_session: AsyncSession):
    """Test that result and error_message are nullable."""
    operation = Operation(
        operation_type="question_generation",
        status="processing",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.result is None
    assert operation.error_message is None


@pytest.mark.asyncio
async def test_operation_large_result(db_session: AsyncSession):
    """Test storing large JSON result."""
    large_result = {
        "question": "A" * 1000,
        "context": "B" * 1000,
        "metadata": {"items": list(range(100))},
    }

    operation = Operation(
        operation_type="question_generation",
        status="completed",
        result=large_result,
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    assert len(operation.result["question"]) == 1000
    assert len(operation.result["context"]) == 1000
    assert len(operation.result["metadata"]["items"]) == 100


@pytest.mark.asyncio
async def test_operation_updated_at_changes(db_session: AsyncSession):
    """Test that updated_at changes when operation is updated."""
    operation = Operation(
        operation_type="question_generation",
        status="pending",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    original_updated_at = operation.updated_at

    # Update the operation
    operation.status = "completed"
    operation.result = {"question": "Test"}
    await db_session.commit()
    await db_session.refresh(operation)

    assert operation.updated_at > original_updated_at
