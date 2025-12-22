# Story 4.8: Create Question Generation Endpoint with Async Pattern

Status: ready-for-dev

## Story

As a user, I want to request a new interview question, so that I can progress
through the interview session.

## Acceptance Criteria

1. **Given** I am authenticated with an active session **When** I POST to
   `/api/v1/sessions/{id}/generate-question` **Then** the system validates I own
   the session and it's active **And** creates an Operation record with
   status='pending' and type='question_generation' **And** returns 202 Accepted
   with operation_id immediately **And** starts a background task to generate
   the question (using dual-context service) **And** updates the Operation
   status to 'processing' then 'completed' with result, or 'failed' with
   error_message **And** if the session is not active, returns 400 Bad Request

## Tasks / Subtasks

- [ ] Task 1: Create background task for question generation (AC: #1)

  - [ ] Create `backend/app/tasks/question_tasks.py` with async task function
  - [ ] Accept operation_id and session_id as parameters
  - [ ] Load session with relationships (job_posting, user.resume)
  - [ ] Update Operation status to 'processing'
  - [ ] Call question_generation_service.generate_question
  - [ ] On success: Update Operation with status='completed' and result
  - [ ] On failure: Update Operation with status='failed' and error_message
  - [ ] Use proper exception handling and logging

- [ ] Task 2: Create generate question endpoint (AC: #1)

  - [ ] Add POST /api/v1/sessions/{id}/generate-question to sessions.py
  - [ ] Validate session exists and belongs to current user
  - [ ] Validate session status is 'active' (not paused or completed)
  - [ ] Create Operation record with type='question_generation',
        status='pending'
  - [ ] Start background task with BackgroundTasks
  - [ ] Return 202 Accepted with operation_id immediately
  - [ ] Return 400 Bad Request if session not active
  - [ ] Return 404 Not Found if session doesn't exist or unauthorized

- [ ] Task 3: Update Operation schema for question generation (AC: #1)

  - [ ] Ensure OperationResponse schema handles question result format
  - [ ] Result should contain: question_text, question_type
  - [ ] Document expected result structure in schema

- [ ] Task 4: Add comprehensive tests (AC: #1)
  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py`
  - [ ] Test successful request returns 202 with operation_id
  - [ ] Test Operation record is created with correct fields
  - [ ] Test background task completes successfully (mock OpenAI)
  - [ ] Test background task updates Operation on success
  - [ ] Test background task handles failures gracefully
  - [ ] Test 400 for non-active session
  - [ ] Test 404 for non-existent or unauthorized session
  - [ ] Test 401 for unauthenticated request

## Dev Notes

### Critical Architecture Requirements

**Async Pattern (STRICT):**

- Endpoint returns 202 Accepted immediately (< 100ms response)
- Long-running OpenAI call happens in background task
- Frontend polls Operation status via story 4.9
- Never block HTTP request waiting for AI generation

**Background Task Pattern:**

- Use FastAPI BackgroundTasks for MVP
- Task updates Operation status throughout execution
- Robust error handling (catch all exceptions)
- Log all errors with context (operation_id, session_id)

**Operation Lifecycle:**

1. pending - Operation created, task not started
2. processing - Task started, generating question
3. completed - Question generated successfully, result stored
4. failed - Error occurred, error_message stored

**API Patterns:**

- 202 Accepted: Operation created, processing asynchronously
- Operation resource location in response body (operation_id)
- Idempotency: Creating multiple operations is allowed (each generates new
  question)

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── api/v1/endpoints/
│   └── sessions.py              # UPDATE - Add generate-question endpoint
├── tasks/
│   └── question_tasks.py        # NEW - Background tasks
└── services/
    └── question_generation_service.py  # EXISTS (from 4.7)
```

**Background Task Implementation:**

```python
# backend/app/tasks/question_tasks.py
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.operation import Operation
from app.models.interview_session import InterviewSession
from app.models.user import User
from app.services.question_generation_service import generate_question
from app.core.database import get_db_session

logger = logging.getLogger(__name__)

async def generate_question_task(operation_id: UUID, session_id: UUID):
    """
    Background task to generate an interview question.

    Args:
        operation_id: UUID of the Operation to update
        session_id: UUID of the InterviewSession
    """
    async with get_db_session() as db:
        try:
            # Load operation
            result = await db.execute(
                select(Operation).where(Operation.id == operation_id)
            )
            operation = result.scalar_one_or_none()

            if not operation:
                logger.error(f"Operation {operation_id} not found")
                return

            # Update to processing
            operation.status = "processing"
            await db.commit()

            # Load session with relationships
            result = await db.execute(
                select(InterviewSession)
                .where(InterviewSession.id == session_id)
                .options(
                    selectinload(InterviewSession.job_posting),
                    selectinload(InterviewSession.user).selectinload(User.resume)
                )
            )
            session = result.scalar_one_or_none()

            if not session:
                logger.error(f"Session {session_id} not found")
                operation.status = "failed"
                operation.error_message = "Session not found"
                await db.commit()
                return

            # Generate question
            question_data = await generate_question(session)

            # Update operation with result
            operation.status = "completed"
            operation.result = question_data
            await db.commit()

            logger.info(f"Question generated successfully for operation {operation_id}")

        except Exception as e:
            logger.error(f"Error in question generation task {operation_id}: {str(e)}", exc_info=True)

            # Update operation with error
            try:
                operation.status = "failed"
                operation.error_message = str(e)
                await db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update operation {operation_id} with error: {commit_error}")
```

**Endpoint Implementation:**

```python
# backend/app/api/v1/endpoints/sessions.py
from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.interview_session import InterviewSession
from app.models.operation import Operation
from app.schemas.operation import OperationResponse
from app.tasks.question_tasks import generate_question_task

router = APIRouter()

@router.post(
    "/{session_id}/generate-question",
    response_model=OperationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate next interview question"
)
async def generate_question(
    session_id: UUID = Path(..., description="Session UUID"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> OperationResponse:
    """
    Generate the next interview question for a session.

    Returns immediately with operation_id. Frontend should poll
    GET /api/v1/operations/{operation_id} to check status.

    - **session_id**: UUID of the active session
    - Returns 202 Accepted with operation_id
    - Returns 400 if session is not active
    - Returns 404 if session not found or unauthorized
    """
    # Load session and validate
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found or you don't have permission to access it"
            }
        )

    # Validate session is active
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_NOT_ACTIVE",
                "message": f"Cannot generate questions for {session.status} session. Only active sessions can receive new questions."
            }
        )

    # Create operation
    operation = Operation(
        operation_type="question_generation",
        status="pending"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    # Start background task
    background_tasks.add_task(
        generate_question_task,
        operation.id,
        session_id
    )

    return OperationResponse.model_validate(operation)
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
import uuid

@pytest.mark.asyncio
async def test_generate_question_returns_operation(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict
):
    """Test question generation returns operation immediately."""
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/generate-question",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 202
    data = response.json()
    assert "id" in data
    assert data["operation_type"] == "question_generation"
    assert data["status"] == "pending"

@pytest.mark.asyncio
@patch('app.tasks.question_tasks.generate_question')
async def test_background_task_completes(
    mock_generate,
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict,
    db: AsyncSession
):
    """Test background task generates question successfully."""
    mock_generate.return_value = {
        "question_text": "Test question?",
        "question_type": "technical"
    }

    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/generate-question",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 202
    operation_id = response.json()["id"]

    # Wait for background task (in tests, might need to manually trigger)
    # Check operation was updated
    operation = await db.get(Operation, uuid.UUID(operation_id))
    await db.refresh(operation)

    # In real test, would need to wait or manually call task
    # assert operation.status == "completed"
    # assert operation.result["question_text"] == "Test question?"

@pytest.mark.asyncio
async def test_generate_question_inactive_session(
    async_client: AsyncClient,
    test_user_token: str,
    test_completed_session: dict
):
    """Test cannot generate question for non-active session."""
    session_id = test_completed_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/generate-question",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    assert "SESSION_NOT_ACTIVE" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_generate_question_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test generating question for non-existent session."""
    fake_id = uuid.uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/generate-question",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_generate_question_unauthorized(
    async_client: AsyncClient
):
    """Test generating question without authentication."""
    fake_id = uuid.uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/generate-question"
    )

    assert response.status_code == 401
```

**Database Session Helper (if needed):**

```python
# backend/app/core/database.py (add context manager for background tasks)
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_session():
    """Get database session for background tasks."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Dependencies

- Requires Operation model from story 4.5
- Requires question_generation_service from story 4.7
- Requires InterviewSession model from story 4.1
- Requires OperationResponse schema from story 4.5

### Related Stories

- Story 4.5: Operation model (stores async operation state)
- Story 4.7: Question generation service (core logic)
- Story 4.9: Operation polling endpoint (frontend checks completion)
- Story 4.10: Store generated question (after this completes)

### Performance Considerations

- Endpoint responds in < 100ms (just creates Operation record)
- Background task takes 5-10 seconds (OpenAI API call)
- Database session per task (isolated from HTTP request)
- No connection pool exhaustion (tasks are short-lived)

### Security Considerations

- Session ownership validated before creating operation
- Only active sessions can generate questions (prevent abuse)
- Background task isolated (no access to HTTP request context)
- Operation results accessible via story 4.9 (also validates ownership)

### Error Handling

- Background task catches all exceptions
- Failed operations have error_message for debugging
- Frontend sees 'failed' status via polling
- Logs include full context (operation_id, session_id, error)

### Testing Challenges

- Background tasks hard to test end-to-end
- May need to call task function directly in tests
- Mock OpenAI service to prevent real API calls
- Consider integration tests with task execution

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Background task patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR59, NFR-P2 (async operations, 10s timeout)

**Key Context Sections:**

- API Patterns: Async operations, 202 Accepted responses
- Background Tasks: FastAPI BackgroundTasks usage
- Error Handling: Robust exception handling in async tasks
