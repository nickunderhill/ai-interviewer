# Story 4.14: Create Session Completion Endpoint

Status: ready-for-dev

## Story

As a user, I want to mark an interview session as complete, so that it moves to
my completed sessions list.

## Acceptance Criteria

1. **Given** I am authenticated with an active or paused session **When** I POST
   to `/api/v1/sessions/{id}/complete` **Then** the system validates I own the
   session **And** updates the session status to 'completed' **And** returns 200
   OK with the updated session **And** the session no longer appears in my
   active sessions **And** appears in completed sessions with all Q&A history
   preserved

## Tasks / Subtasks

- [ ] Task 1: Create session completion endpoint (AC: #1)

  - [ ] Add POST /api/v1/sessions/{id}/complete to sessions.py router
  - [ ] Use path parameter for session UUID
  - [ ] Use get_current_user dependency for authentication
  - [ ] Validate session exists and belongs to user
  - [ ] Validate session is 'active' or 'paused' (not already completed)
  - [ ] Update session status to 'completed'
  - [ ] Return 200 OK with SessionResponse
  - [ ] Return 400 Bad Request if session already completed
  - [ ] Return 404 Not Found if session doesn't exist or unauthorized

- [ ] Task 2: Verify completed sessions filtering (AC: #1)

  - [ ] Verify GET /api/v1/sessions?status=active excludes completed
  - [ ] Verify GET /api/v1/sessions?status=completed includes only completed
  - [ ] Document that completed sessions preserve all data

- [ ] Task 3: Add comprehensive tests (AC: #1)
  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py`
  - [ ] Test completing active session updates status
  - [ ] Test completing paused session updates status
  - [ ] Test cannot complete already completed session
  - [ ] Test completed session appears in completed list
  - [ ] Test completed session not in active list
  - [ ] Test completed session messages preserved
  - [ ] Test 404 for non-existent session
  - [ ] Test 401 for unauthenticated request

## Dev Notes

### Critical Architecture Requirements

**Session State Machine (FINAL STATE):**

- active → completed (user finishes interview)
- paused → completed (user finishes paused interview)
- completed → completed (no further transitions)
- Completed is terminal state (cannot revert)

**Data Preservation (CRITICAL):**

- Completed sessions preserve ALL data:
  - Session metadata (id, timestamps, question_number)
  - Job posting reference (FK preserved even if posting deleted)
  - All SessionMessage records (complete Q&A history)
  - User can review completed sessions anytime

**Filtering Behavior:**

- Active sessions list: status='active' only
- Paused sessions: status='paused' only
- Completed sessions: status='completed' only
- All sessions: no status filter (includes all)

### Technical Implementation Details

**File Structure:**

```
backend/app/
└── api/v1/endpoints/
    └── sessions.py              # UPDATE - Add complete endpoint
```

**Completion Endpoint Implementation:**

```python
# backend/app/api/v1/endpoints/sessions.py
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.interview_session import InterviewSession
from app.schemas.session import SessionResponse

router = APIRouter()

@router.post(
    "/{session_id}/complete",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark session as completed"
)
async def complete_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionResponse:
    """
    Mark an interview session as completed.

    This is the final state for a session. Completed sessions:
    - Cannot be modified or resumed
    - Preserve all Q&A history
    - Appear in completed sessions list
    - Can be viewed for review anytime

    - **session_id**: UUID of the session
    - Returns updated session with status='completed'
    - Returns 400 if session is already completed
    - Returns 404 if session not found or unauthorized
    """
    # Load and validate session
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

    # Validate session is not already completed
    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_ALREADY_COMPLETED",
                "message": "Session is already completed. Completed sessions cannot be modified."
            }
        )

    # Update status to completed
    session.status = "completed"
    await db.commit()
    await db.refresh(session)

    return SessionResponse.model_validate(session)
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.interview_session import InterviewSession
from app.models.session_message import SessionMessage

@pytest.mark.asyncio
async def test_complete_active_session_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict,
    db: AsyncSession
):
    """Test completing an active session."""
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

    # Verify in database
    session = await db.get(InterviewSession, uuid.UUID(session_id))
    await db.refresh(session)
    assert session.status == "completed"

@pytest.mark.asyncio
async def test_complete_paused_session_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_paused_session: dict,
    db: AsyncSession
):
    """Test completing a paused session."""
    session_id = test_paused_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"

@pytest.mark.asyncio
async def test_complete_already_completed_session_fails(
    async_client: AsyncClient,
    test_user_token: str,
    test_completed_session: dict
):
    """Test cannot complete already completed session."""
    session_id = test_completed_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    assert "SESSION_ALREADY_COMPLETED" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_completed_session_appears_in_filter(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict
):
    """Test completed session appears in completed list."""
    session_id = test_active_session["id"]

    # Complete the session
    await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Check active sessions - should not include completed
    response1 = await async_client.get(
        "/api/v1/sessions?status=active",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    active_sessions = response1.json()
    assert not any(s["id"] == session_id for s in active_sessions)

    # Check completed sessions - should include it
    response2 = await async_client.get(
        "/api/v1/sessions?status=completed",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    completed_sessions = response2.json()
    assert any(s["id"] == session_id for s in completed_sessions)

@pytest.mark.asyncio
async def test_completed_session_preserves_messages(
    async_client: AsyncClient,
    test_user_token: str,
    test_session_with_messages: dict,
    db: AsyncSession
):
    """Test completing session preserves all messages."""
    session_id = test_session_with_messages["id"]

    # Get messages before completion
    response1 = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    messages_before = response1.json()
    message_count_before = len(messages_before)

    # Complete session
    await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get messages after completion
    response2 = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    messages_after = response2.json()

    # Verify messages unchanged
    assert len(messages_after) == message_count_before
    assert messages_after == messages_before

@pytest.mark.asyncio
async def test_complete_session_workflow(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session_full: dict
):
    """Test complete workflow: create, Q&A, complete."""
    session_id = test_active_session_full["id"]

    # Session is active with some Q&A
    response1 = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.json()["status"] == "active"

    # User completes interview
    response2 = await async_client.post(
        f"/api/v1/sessions/{session_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "completed"

    # Verify can still view session details
    response3 = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response3.status_code == 200
    assert response3.json()["status"] == "completed"

    # Verify can still view messages
    response4 = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response4.status_code == 200
    assert len(response4.json()) > 0

@pytest.mark.asyncio
async def test_complete_session_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test completing non-existent session."""
    fake_id = uuid.uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/complete",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_complete_session_unauthorized(async_client: AsyncClient):
    """Test completing session without authentication."""
    fake_id = uuid.uuid4()

    response = await async_client.post(f"/api/v1/sessions/{fake_id}/complete")

    assert response.status_code == 401
```

**Test Fixtures:**

```python
# backend/tests/conftest.py (add fixture)
@pytest.fixture
async def test_completed_session(
    db: AsyncSession,
    test_user: User,
    test_job_posting: JobPosting
):
    """Create a completed session."""
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="completed",
        current_question_number=5
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {"id": session.id}
```

### Dependencies

- Requires InterviewSession model from story 4.1
- Requires SessionResponse schema from story 4.2
- Requires session list endpoint from story 4.3 (filtering)
- Requires messages endpoint from story 4.12 (history preservation)

### Related Stories

- Story 4.1: Session model with status field
- Story 4.3: Session list with filtering (uses completed status)
- Story 4.13: Session pause/resume (other status transitions)
- Epic 6: Session history and review (reads completed sessions)
- Epic 7: Interview retakes (creates new sessions for same job)

### Session Lifecycle Summary

```
┌─────────┐
│ CREATE  │
└────┬────┘
     │
     v
┌─────────┐     pause      ┌─────────┐
│ ACTIVE  │ ────────────> │ PAUSED  │
└─┬───┬───┘                └────┬────┘
  │   │         resume          │
  │   │ <───────────────────────┘
  │   │
  │   │ complete
  │   v
  │ ┌───────────┐
  │ │ COMPLETED │
  │ └───────────┘
  │       ^
  │       │ complete
  └───────┘

NOTES:
- ACTIVE: Can generate questions, submit answers, pause, complete
- PAUSED: Can only resume or complete
- COMPLETED: Terminal state, read-only
```

### Frontend Integration

**Completion Triggers:**

- User clicks "End Interview" button
- User completes desired number of questions
- User wants to review past sessions

**Post-Completion Actions:**

- Redirect to completed sessions list
- Show completion summary (questions answered, time spent)
- Offer to start new session (retake)
- Enable review mode (view Q&A history)

### Data Integrity

- Status update is atomic (single field change)
- Messages FK relationship preserved (cascade or SET NULL)
- Job posting reference preserved (even if posting deleted via SET NULL from
  story 4.1)
- Timestamps track session duration (created_at to updated_at)

### Design Decisions

**Why POST not PUT?**

- Completion is an action/command, not a field update
- Signals important state transition
- Allows future expansion (e.g., completion metadata)
- Follows RESTful resource action pattern

**Why allow completing paused sessions?**

- User might pause, review, and decide to complete without resuming
- Flexible workflow (not forcing resume → complete path)
- Simpler logic (both active and paused can complete)

**Why completed is terminal?**

- Prevents accidental modification of historical data
- Clear separation between in-progress and archived sessions
- Enables different UI/UX for review vs. active interviews
- Future: Could add "reopen" feature if needed

**Why preserve all data?**

- Required for session history review (FR45-46)
- Required for progress tracking (FR47-49)
- Required for retake comparison (FR54-56)
- Historical data is valuable for improvement tracking

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  State machine patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR22, FR45-46 (session status, history preservation)

**Key Context Sections:**

- Session State: Terminal states, data preservation
- API Patterns: POST for actions, idempotency
- Frontend Integration: Completion workflows
