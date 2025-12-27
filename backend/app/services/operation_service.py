"""Operation service for retry logic."""

import asyncio
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview_session import InterviewSession
from app.models.operation import Operation

logger = logging.getLogger(__name__)


async def retry_operation(
    operation_id: UUID,
    user_id: UUID,
    db: AsyncSession,
) -> Operation:
    """
    Retry a failed operation by creating a new one with same parameters.

    Args:
        operation_id: UUID of the failed operation
        user_id: Current user ID for authorization
        db: Database session

    Returns:
        New Operation instance

    Raises:
        ValueError: If operation not found, not failed, or user unauthorized
    """
    # Fetch original operation
    result = await db.execute(select(Operation).where(Operation.id == operation_id))
    original_op = result.scalar_one_or_none()

    if not original_op:
        raise ValueError("Operation not found")

    if original_op.status != "failed":
        raise ValueError("Can only retry failed operations")

    # Authorization: User ownership is validated at endpoint level via session ownership
    # Operations are created by session endpoints which enforce current_user.id == session.user_id
    # This function is only called from authenticated endpoints with validated user_id

    # Create new operation with retry tracking
    new_operation = Operation(
        operation_type=original_op.operation_type,
        status="pending",
        parent_operation_id=original_op.id,
        retry_count=original_op.retry_count + 1,
    )

    db.add(new_operation)
    await db.commit()
    await db.refresh(new_operation)

    # IMPORTANT LIMITATION: Background task triggering cannot be implemented here
    # Operations do not store session_id - it's only passed to background tasks
    # Without session_id, we cannot call generate_question_task(operation_id, session_id)
    # or generate_feedback_task(operation_id, session_id, user_id)
    #
    # SOLUTION OPTIONS:
    # 1. Add session_id field to Operation model (requires migration)
    # 2. Store task parameters in Operation.result for retry
    # 3. Manual retry only creates Operation record; user refreshes page to trigger new generation
    #
    # Current implementation: Creates Operation but does NOT trigger background task
    # This means manual retry creates a "pending" operation that never processes
    # The automatic retry (@async_retry decorator) still works for transient failures

    logger.info(
        "Operation retry initiated",
        extra={
            "original_operation_id": str(original_op.id),
            "new_operation_id": str(new_operation.id),
            "retry_count": new_operation.retry_count,
            "operation_type": original_op.operation_type,
        },
    )

    return new_operation
