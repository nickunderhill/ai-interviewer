"""Tests for generate question endpoint."""

from unittest.mock import patch
from uuid import UUID, uuid4

from httpx import AsyncClient
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.operation import Operation


@pytest.mark.asyncio
async def test_generate_question_returns_operation(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test question generation returns operation immediately."""
    response = await async_client.post(
        f"/api/v1/sessions/{test_active_session['id']}/generate-question",
        headers=auth_headers,
    )

    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["operation_type"] == "question_generation"
    assert data["status"] == "pending"

    # Verify operation was created in database
    operation_id = UUID(data["id"])
    result = await db_session.execute(
        select(Operation).where(Operation.id == operation_id)
    )
    operation = result.scalar_one_or_none()
    assert operation is not None
    assert operation.operation_type == "question_generation"


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_background_task_completes_successfully(
    mock_generate,
    mock_session_local,
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test background task generates question successfully."""
    # Configure mock to use the test's db_session
    mock_session_local.return_value.__aenter__.return_value = db_session

    mock_generate.return_value = {
        "question_text": "What is your experience with Python?",
        "question_type": "technical",
    }

    # Import and call task directly to test it
    from app.tasks.question_tasks import generate_question_task

    # Create operation manually
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Run background task
    await generate_question_task(operation.id, test_active_session["id"])

    # Verify operation was updated
    await db_session.refresh(operation)
    assert operation.status == "completed"
    assert operation.result["question_text"] == "What is your experience with Python?"
    assert operation.result["question_type"] == "technical"


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
async def test_background_task_handles_session_not_found(
    mock_session_local,
    async_client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
):
    """Test background task handles missing session."""
    # Configure mock to use the test's db_session
    mock_session_local.return_value.__aenter__.return_value = db_session

    from app.tasks.question_tasks import generate_question_task

    # Create operation
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Run task with non-existent session
    fake_session_id = uuid4()
    await generate_question_task(operation.id, fake_session_id)

    # Verify operation was marked as failed
    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert "Session not found" in operation.error_message


@pytest.mark.asyncio
@patch("app.tasks.question_tasks.AsyncSessionLocal")
@patch("app.tasks.question_tasks.generate_question")
async def test_background_task_handles_generation_error(
    mock_generate,
    mock_session_local,
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test background task handles OpenAI errors gracefully."""
    # Configure mock to use the test's db_session
    mock_session_local.return_value.__aenter__.return_value = db_session
    mock_generate.side_effect = Exception("OpenAI API error")

    from app.tasks.question_tasks import generate_question_task

    # Create operation
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Run background task
    await generate_question_task(operation.id, test_active_session["id"])

    # Verify operation was marked as failed
    await db_session.refresh(operation)
    assert operation.status == "failed"
    assert "OpenAI API error" in operation.error_message


@pytest.mark.asyncio
async def test_generate_question_inactive_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_completed_session: dict,
):
    """Test cannot generate question for non-active session."""
    response = await async_client.post(
        f"/api/v1/sessions/{test_completed_session['id']}/generate-question",
        headers=auth_headers,
    )

    assert response.status_code == 400
    data = response.json()
    assert "SESSION_NOT_ACTIVE" in data["detail"]["code"]
    assert "completed" in data["detail"]["message"]


@pytest.mark.asyncio
async def test_generate_question_paused_session(
    async_client: AsyncClient,
    auth_headers: dict,
    test_paused_session: dict,
):
    """Test cannot generate question for paused session."""
    response = await async_client.post(
        f"/api/v1/sessions/{test_paused_session['id']}/generate-question",
        headers=auth_headers,
    )

    assert response.status_code == 400
    data = response.json()
    assert "SESSION_NOT_ACTIVE" in data["detail"]["code"]


@pytest.mark.asyncio
async def test_generate_question_not_found(
    async_client: AsyncClient, auth_headers: dict
):
    """Test generating question for non-existent session."""
    fake_id = uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/generate-question",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "SESSION_NOT_FOUND" in data["detail"]["code"]


@pytest.mark.asyncio
async def test_generate_question_unauthorized_session(
    async_client: AsyncClient,
    auth_headers: dict,
    other_user_session: dict,
):
    """Test cannot generate question for another user's session."""
    response = await async_client.post(
        f"/api/v1/sessions/{other_user_session['id']}/generate-question",
        headers=auth_headers,
    )

    assert response.status_code == 404
    data = response.json()
    assert "SESSION_NOT_FOUND" in data["detail"]["code"]


@pytest.mark.asyncio
async def test_generate_question_unauthenticated(async_client: AsyncClient):
    """Test generating question without authentication."""
    fake_id = uuid4()

    response = await async_client.post(f"/api/v1/sessions/{fake_id}/generate-question")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_generate_question_updates_operation_to_processing(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test background task updates operation to processing status."""
    from app.tasks.question_tasks import generate_question_task

    # Create operation
    operation = Operation(operation_type="question_generation", status="pending")
    db_session.add(operation)
    await db_session.commit()
    await db_session.refresh(operation)

    # Mock generate_question to pause and check status
    with patch("app.tasks.question_tasks.generate_question") as mock_generate:
        # Setup mock that allows us to check operation mid-execution
        async def check_processing(*args, **kwargs):
            # At this point, operation should be 'processing'
            await db_session.refresh(operation)
            assert operation.status == "processing"
            return {
                "question_text": "Test question?",
                "question_type": "technical",
            }

        mock_generate.side_effect = check_processing

        # Run task
        await generate_question_task(operation.id, test_active_session["id"])


@pytest.mark.asyncio
async def test_generate_question_multiple_operations_allowed(
    async_client: AsyncClient,
    auth_headers: dict,
    test_active_session: dict,
    db_session: AsyncSession,
):
    """Test can create multiple question generation operations for same session."""
    # First request
    response1 = await async_client.post(
        f"/api/v1/sessions/{test_active_session['id']}/generate-question",
        headers=auth_headers,
    )
    assert response1.status_code == 202
    operation_id_1 = response1.json()["id"]

    # Second request
    response2 = await async_client.post(
        f"/api/v1/sessions/{test_active_session['id']}/generate-question",
        headers=auth_headers,
    )
    assert response2.status_code == 202
    operation_id_2 = response2.json()["id"]

    # Both operations should exist and have different IDs
    assert operation_id_1 != operation_id_2

    # Verify both operations exist in database
    result = await db_session.execute(
        select(Operation).where(
            Operation.id.in_([UUID(operation_id_1), UUID(operation_id_2)])
        )
    )
    operations = result.scalars().all()
    assert len(operations) == 2
