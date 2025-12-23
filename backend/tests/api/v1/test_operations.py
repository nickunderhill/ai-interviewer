"""Tests for operations API endpoints."""

import pytest
from uuid import UUID, uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation import Operation


@pytest.mark.asyncio
async def test_get_operation_pending(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test retrieving pending operation."""
    # Create pending operation
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(operation.id)
    assert data["status"] == "pending"
    assert data["result"] is None
    assert data["error_message"] is None


@pytest.mark.asyncio
async def test_get_operation_processing(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test retrieving processing operation."""
    operation = Operation(operation_type="question_generation", status="processing")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["result"] is None


@pytest.mark.asyncio
async def test_get_operation_completed_with_result(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test retrieving completed operation with result data."""
    result_data = {
        "question_text": "What is your experience with Python?",
        "question_type": "technical",
    }
    operation = Operation(
        operation_type="question_generation", status="completed", result=result_data
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["result"] == result_data
    assert data["error_message"] is None


@pytest.mark.asyncio
async def test_get_operation_failed_with_error(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test retrieving failed operation with error message."""
    operation = Operation(
        operation_type="question_generation",
        status="failed",
        error_message="OpenAI API error: Rate limit exceeded",
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["result"] is None
    assert "Rate limit exceeded" in data["error_message"]


@pytest.mark.asyncio
async def test_get_operation_not_found(async_client: AsyncClient):
    """Test 404 for non-existent operation."""
    fake_id = uuid4()

    response = await async_client.get(f"/api/v1/operations/{fake_id}")

    assert response.status_code == 404
    data = response.json()
    assert "OPERATION_NOT_FOUND" in data["detail"]["code"]


@pytest.mark.asyncio
async def test_polling_pattern_status_updates(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test polling pattern - multiple requests show status changes."""
    # Create pending operation
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # First poll - pending
    response1 = await async_client.get(f"/api/v1/operations/{operation.id}")
    assert response1.status_code == 200
    assert response1.json()["status"] == "pending"

    # Simulate status update to processing
    operation.status = "processing"
    await db_session.commit()

    # Second poll - processing
    response2 = await async_client.get(f"/api/v1/operations/{operation.id}")
    assert response2.status_code == 200
    assert response2.json()["status"] == "processing"

    # Simulate completion
    operation.status = "completed"
    operation.result = {"question_text": "Test question", "question_type": "technical"}
    await db_session.commit()

    # Third poll - completed
    response3 = await async_client.get(f"/api/v1/operations/{operation.id}")
    assert response3.status_code == 200
    data = response3.json()
    assert data["status"] == "completed"
    assert data["result"]["question_text"] == "Test question"


@pytest.mark.asyncio
async def test_operation_idempotent_polling(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Test that polling same operation multiple times is idempotent."""
    operation = Operation(
        operation_type="question_generation",
        status="completed",
        result={"question_text": "Same question", "question_type": "behavioral"},
    )
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Poll multiple times
    responses = []
    for _ in range(5):
        response = await async_client.get(f"/api/v1/operations/{operation.id}")
        responses.append(response)

    # All responses should be identical
    assert all(r.status_code == 200 for r in responses)
    data_list = [r.json() for r in responses]
    assert all(d["status"] == "completed" for d in data_list)
    assert all(d["result"]["question_text"] == "Same question" for d in data_list)
