"""Test Operation model retry tracking fields."""

import pytest
from sqlalchemy import select

from app.models.operation import Operation


@pytest.mark.asyncio
async def test_operation_retry_fields_exist(db_session):
    """Test that retry tracking fields are available on Operation model."""
    # Create parent operation
    parent_op = Operation(
        operation_type="question_generation",
        status="failed",
        error_message="Connection timeout",
    )
    db_session.add(parent_op)
    await db_session.commit()
    await db_session.refresh(parent_op)

    # Create child operation (retry) with parent_id and retry_count
    retry_op = Operation(
        operation_type="question_generation",
        status="pending",
        parent_operation_id=parent_op.id,
        retry_count=1,
    )
    db_session.add(retry_op)
    await db_session.commit()
    await db_session.refresh(retry_op)

    # Verify fields are set
    assert retry_op.parent_operation_id == parent_op.id
    assert retry_op.retry_count == 1

    # Verify default retry_count for parent
    assert parent_op.retry_count == 0

    # Verify relationship works
    result = await db_session.execute(
        select(Operation).where(Operation.parent_operation_id == parent_op.id)
    )
    retries = result.scalars().all()
    assert len(retries) == 1
    assert retries[0].id == retry_op.id
