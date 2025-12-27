"""Test operations retry endpoint."""

from httpx import AsyncClient
import pytest
from sqlalchemy import select

from app.models.interview_session import InterviewSession
from app.models.operation import Operation


@pytest.mark.asyncio
async def test_retry_failed_operation_creates_new_operation(
    async_client: AsyncClient,
    auth_headers: dict,
    test_session: InterviewSession,
    db_session,
):
    """Test that retrying a failed operation creates a new operation."""
    # Create a failed operation
    failed_op = Operation(
        operation_type="question_generation",
        status="failed",
        error_message="Network timeout",
    )
    db_session.add(failed_op)
    await db_session.commit()
    await db_session.refresh(failed_op)

    # Retry the operation
    response = await async_client.post(
        f"/api/v1/operations/{failed_op.id}/retry",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    # Verify new operation created with parent reference
    assert data["id"] != str(failed_op.id)
    assert data["parent_operation_id"] == str(failed_op.id)
    assert data["retry_count"] == 1
    assert data["status"] == "pending"
    assert data["operation_type"] == "question_generation"

    # Verify in database
    result = await db_session.execute(select(Operation).where(Operation.id == data["id"]))
    new_op = result.scalar_one()
    assert new_op.parent_operation_id == failed_op.id
    assert new_op.retry_count == 1


@pytest.mark.asyncio
async def test_retry_non_failed_operation_returns_error(
    async_client: AsyncClient,
    auth_headers: dict,
    db_session,
):
    """Test that retrying a non-failed operation returns 400."""
    # Create a completed operation
    completed_op = Operation(
        operation_type="question_generation",
        status="completed",
        result={"question": "test"},
    )
    db_session.add(completed_op)
    await db_session.commit()
    await db_session.refresh(completed_op)

    # Attempt retry
    response = await async_client.post(
        f"/api/v1/operations/{completed_op.id}/retry",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "only retry failed operations" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_retry_nonexistent_operation_returns_404(
    async_client: AsyncClient,
    auth_headers: dict,
):
    """Test that retrying a non-existent operation returns 404."""
    response = await async_client.post(
        "/api/v1/operations/00000000-0000-0000-0000-000000000000/retry",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()
