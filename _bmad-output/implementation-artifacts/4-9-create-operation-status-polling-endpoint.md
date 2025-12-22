# Story 4.9: Create Operation Status Polling Endpoint

Status: ready-for-dev

## Story

As a user, I want to poll the status of question generation, so that I know when
the AI-generated question is ready.

## Acceptance Criteria

1. **Given** I have initiated a question generation operation **When** I GET
   `/api/v1/operations/{operation_id}` every 2-3 seconds **Then** the system
   returns the operation with current status, result (if completed), or
   error_message (if failed) **And** returns 200 OK **And** the frontend polls
   until status is 'completed' or 'failed' **And** if the operation doesn't
   exist, returns 404 Not Found

## Tasks / Subtasks

- [ ] Task 1: Create operations endpoint file (AC: #1)

  - [ ] Create `backend/app/api/v1/endpoints/operations.py` with APIRouter
  - [ ] Set up router with prefix and tags
  - [ ] Import necessary dependencies (get_db, models, schemas)

- [ ] Task 2: Implement get operation by ID endpoint (AC: #1)

  - [ ] Create GET /api/v1/operations/{operation_id} endpoint
  - [ ] Accept operation_id as UUID path parameter
  - [ ] Query Operation by id
  - [ ] Return 200 OK with OperationResponse (includes status, result,
        error_message)
  - [ ] Return 404 Not Found if operation doesn't exist
  - [ ] No authentication required (operations are short-lived, no sensitive
        data)

- [ ] Task 3: Register operations router (AC: #1)

  - [ ] Import operations router in `backend/app/api/v1/api.py`
  - [ ] Register with prefix /operations and tag "operations"
  - [ ] Verify endpoint accessible at /api/v1/operations/{id}

- [ ] Task 4: Add comprehensive tests (AC: #1)
  - [ ] Create `backend/tests/api/v1/test_operations.py`
  - [ ] Test pending operation returns correct status
  - [ ] Test processing operation returns correct status
  - [ ] Test completed operation returns result data
  - [ ] Test failed operation returns error_message
  - [ ] Test 404 for non-existent operation
  - [ ] Test polling pattern (multiple requests return updated status)

## Dev Notes

### Critical Architecture Requirements

**Polling Pattern (STRICT):**

- Frontend polls every 2-3 seconds (not faster to avoid overload)
- Poll until status is 'completed' or 'failed'
- Stop polling on completion or failure
- Display loading indicator during polling

**API Patterns:**

- GET endpoint (idempotent, safe for repeated calls)
- No authentication required for MVP (operations are public by ID)
- 200 OK for all valid operation IDs
- Result field contains operation-specific data (question, feedback, etc.)

**Security Considerations:**

- Operations are short-lived (minutes, not hours)
- No sensitive data in operation results (user's own data only)
- Operation IDs are UUIDs (not guessable)
- Future: Add user_id to Operation model for user-specific access

### Technical Implementation Details

**File Structure:**

```
backend/app/
└── api/v1/endpoints/
    ├── operations.py            # NEW - Operations endpoints
    └── __init__.py              # Import operations router
```

**Operations Endpoint Implementation:**

```python
# backend/app/api/v1/endpoints/operations.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.operation import Operation
from app.schemas.operation import OperationResponse

router = APIRouter()

@router.get(
    "/{operation_id}",
    response_model=OperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get operation status"
)
async def get_operation_status(
    operation_id: UUID = Path(..., description="Operation UUID"),
    db: AsyncSession = Depends(get_db)
) -> OperationResponse:
    """
    Get the current status of an async operation.

    Frontend should poll this endpoint every 2-3 seconds until
    status is 'completed' or 'failed'.

    - **operation_id**: UUID of the operation
    - Returns operation with status and result/error_message
    - Returns 404 if operation not found
    """
    result = await db.execute(
        select(Operation).where(Operation.id == operation_id)
    )
    operation = result.scalar_one_or_none()

    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "OPERATION_NOT_FOUND",
                "message": "Operation not found. It may have expired or never existed."
            }
        )

    return OperationResponse.model_validate(operation)
```

**Router Registration:**

```python
# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import operations, sessions, users

api_router = APIRouter()

api_router.include_router(
    operations.router,
    prefix="/operations",
    tags=["operations"]
)

api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["sessions"]
)

# ... other routers
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_operations.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.operation import Operation

@pytest.mark.asyncio
async def test_get_operation_pending(
    async_client: AsyncClient,
    db: AsyncSession
):
    """Test retrieving pending operation."""
    # Create pending operation
    operation = Operation(
        operation_type="question_generation",
        status="pending"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(operation.id)
    assert data["status"] == "pending"
    assert data["result"] is None

@pytest.mark.asyncio
async def test_get_operation_completed(
    async_client: AsyncClient,
    db: AsyncSession
):
    """Test retrieving completed operation with result."""
    # Create completed operation
    result_data = {
        "question_text": "What is Python?",
        "question_type": "technical"
    }

    operation = Operation(
        operation_type="question_generation",
        status="completed",
        result=result_data
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["result"]["question_text"] == "What is Python?"
    assert data["result"]["question_type"] == "technical"

@pytest.mark.asyncio
async def test_get_operation_failed(
    async_client: AsyncClient,
    db: AsyncSession
):
    """Test retrieving failed operation with error message."""
    operation = Operation(
        operation_type="question_generation",
        status="failed",
        error_message="OpenAI API rate limit exceeded"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    response = await async_client.get(f"/api/v1/operations/{operation.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error_message"] == "OpenAI API rate limit exceeded"

@pytest.mark.asyncio
async def test_get_operation_not_found(async_client: AsyncClient):
    """Test retrieving non-existent operation."""
    fake_id = uuid.uuid4()

    response = await async_client.get(f"/api/v1/operations/{fake_id}")

    assert response.status_code == 404
    assert "OPERATION_NOT_FOUND" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_polling_pattern_status_updates(
    async_client: AsyncClient,
    db: AsyncSession
):
    """Test that polling sees status updates."""
    # Create pending operation
    operation = Operation(
        operation_type="question_generation",
        status="pending"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    # First poll - pending
    response1 = await async_client.get(f"/api/v1/operations/{operation.id}")
    assert response1.json()["status"] == "pending"

    # Update operation status
    operation.status = "processing"
    await db.commit()

    # Second poll - processing
    response2 = await async_client.get(f"/api/v1/operations/{operation.id}")
    assert response2.json()["status"] == "processing"

    # Update to completed with result
    operation.status = "completed"
    operation.result = {"question_text": "Test", "question_type": "technical"}
    await db.commit()

    # Third poll - completed
    response3 = await async_client.get(f"/api/v1/operations/{operation.id}")
    assert response3.json()["status"] == "completed"
    assert response3.json()["result"] is not None
```

**Frontend Polling Pattern (Reference):**

```typescript
// Example frontend polling logic (NOT part of backend story)
async function pollOperationStatus(
  operationId: string
): Promise<OperationResult> {
  const maxAttempts = 60; // 3 minutes max (60 * 3 seconds)
  let attempts = 0;

  while (attempts < maxAttempts) {
    const response = await fetch(`/api/v1/operations/${operationId}`);
    const operation = await response.json();

    if (operation.status === 'completed') {
      return operation.result;
    }

    if (operation.status === 'failed') {
      throw new Error(operation.error_message);
    }

    // Still pending or processing - wait and retry
    await new Promise(resolve => setTimeout(resolve, 2500)); // 2.5 seconds
    attempts++;
  }

  throw new Error('Operation timed out');
}
```

### Dependencies

- Requires Operation model from story 4.5
- Requires OperationResponse schema from story 4.5
- Used by frontend after story 4.8 creates operations

### Related Stories

- Story 4.5: Operation model (data structure)
- Story 4.8: Creates operations (this endpoint reads them)
- Story 5.3: Feedback operations (also polled via this endpoint)
- Frontend polling: Story 4.8 frontend integration

### Performance Considerations

- Simple query by primary key (UUID) - very fast
- No authentication overhead (public endpoint)
- Polling every 2-3 seconds acceptable load (< 1 req/sec per user)
- Operation records small (< 1KB typically)
- Consider adding cleanup job for old operations (future)

### Security Considerations

**No Authentication Required (MVP):**

- Operations are short-lived (minutes)
- Operation IDs are UUIDs (not guessable)
- No sensitive data in results (user's own generated content)
- Future: Add user_id to Operation and validate ownership

**Rate Limiting (Future):**

- Consider rate limiting polling endpoint
- Prevent abuse (polling too frequently)
- Not critical for MVP with small user base

### Design Decisions

**Why no authentication?**

- Simplifies frontend polling (no token refresh issues)
- Operations are public by their UUID
- No sensitive data exposure risk
- Can add authentication later if needed

**Why not WebSockets?**

- Polling is simpler for MVP
- Works with all infrastructure (no WebSocket support needed)
- Acceptable latency (2-3 second updates)
- Easier to test and debug

**Why not server-sent events (SSE)?**

- Similar to polling but more complex
- Not all infrastructure supports SSE
- Polling is more universal
- SSE is future enhancement

### Error Handling

- 404 for non-existent operations
- Clear error messages in failed operations
- Frontend should handle timeout (stop polling after N attempts)
- Log polling requests for monitoring (optional)

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  API patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR59, NFR-P3 (polling pattern, 2-3 seconds)

**Key Context Sections:**

- API Patterns: GET endpoints, polling patterns
- Performance: Query optimization, acceptable polling rates
- Testing: Async endpoint testing
