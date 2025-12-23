# Story 4.13: Create Session Resume Capability

Status: review

## Story

As a user, I want to resume an interrupted interview session, so that I don't
lose progress if I close my browser.

## Acceptance Criteria

1. **Given** I am authenticated and have an active or paused session **When** I
   access the session through `/api/v1/sessions/{id}` **Then** the system
   returns the full session context including all previous messages **And** the
   frontend can reconstruct the UI state from current_question_number and
   message history **And** I can continue from where I left off **And** if I
   manually pause, the session status updates to 'paused' **And** paused
   sessions can be resumed later

## Tasks / Subtasks

- [x] Task 1: Create session pause endpoint (AC: #1)

  - [x] Add PUT /api/v1/sessions/{id}/pause to sessions.py router
  - [x] Validate session exists and belongs to user
  - [x] Validate session is currently 'active' (can't pause completed session)
  - [x] Update session status to 'paused'
  - [x] Return 200 OK with updated session
  - [x] Return 400 Bad Request if session not active

- [x] Task 2: Create session resume endpoint (AC: #1)

  - [x] Add PUT /api/v1/sessions/{id}/resume to sessions.py router
  - [x] Validate session exists and belongs to user
  - [x] Validate session is currently 'paused'
  - [x] Update session status to 'active'
  - [x] Return 200 OK with updated session
  - [x] Return 400 Bad Request if session not paused

- [x] Task 3: Enhance session detail endpoint for resume (AC: #1)

    - [x] Verify GET /api/v1/sessions/{id} returns all resume context
    - [x] Ensure includes: session metadata, job_posting, resume, messages
    - [x] Document frontend requirements for resume:
    - Check session.status ('active' or 'paused')
    - Get current_question_number for progress
    - Load messages via /api/v1/sessions/{id}/messages
    - Reconstruct conversation UI

- [x] Task 4: Add comprehensive tests (AC: #1)
    - [x] Add tests to `backend/tests/api/v1/test_sessions.py`
    - [x] Test pausing active session updates status
    - [x] Test resuming paused session updates status
    - [x] Test cannot pause completed session
    - [x] Test cannot resume active session
    - [x] Test session detail provides full context
    - [x] Test 404 for non-existent session
    - [x] Test 401 for unauthenticated request

## Dev Notes

### Critical Architecture Requirements

**Session State Machine:**

- active → paused (manual pause)
- paused → active (resume)
- active → completed (manual completion, story 4.14)
- Cannot pause completed sessions
- Cannot resume active or completed sessions

**Resume Context:**

- Session metadata: id, status, current_question_number, timestamps
- Job posting: Full details (title, description, tech_stack, etc.)
- Resume: User's resume content
- Messages: All Q&A history in chronological order

**Persistence (CRITICAL):**

- State persists across browser close/refresh
- No server-side session storage (JWT-based auth)
- Frontend reconstructs UI from API data
- Messages persist in database (story 4.10, 4.11)

### Technical Implementation Details

**File Structure:**

```
backend/app/
└── api/v1/endpoints/
    └── sessions.py              # UPDATE - Add pause/resume endpoints
```

**Pause Endpoint Implementation:**

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

@router.put(
    "/{session_id}/pause",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Pause an active session"
)
async def pause_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionResponse:
    """
    Pause an active interview session.

    - **session_id**: UUID of the session
    - Returns updated session with status='paused'
    - Returns 400 if session is not active
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

    # Validate session is active
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SESSION_STATE",
                "message": f"Cannot pause {session.status} session. Only active sessions can be paused."
            }
        )

    # Update status
    session.status = "paused"
    await db.commit()
    await db.refresh(session)

    return SessionResponse.model_validate(session)

@router.put(
    "/{session_id}/resume",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Resume a paused session"
)
async def resume_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionResponse:
    """
    Resume a paused interview session.

    - **session_id**: UUID of the session
    - Returns updated session with status='active'
    - Returns 400 if session is not paused
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

    # Validate session is paused
    if session.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SESSION_STATE",
                "message": f"Cannot resume {session.status} session. Only paused sessions can be resumed."
            }
        )

    # Update status
    session.status = "active"
    await db.commit()
    await db.refresh(session)

    return SessionResponse.model_validate(session)
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_pause_session_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict,
    db: AsyncSession
):
    """Test pausing an active session."""
    session_id = test_active_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/pause",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "paused"

    # Verify in database
    session = await db.get(InterviewSession, uuid.UUID(session_id))
    await db.refresh(session)
    assert session.status == "paused"

@pytest.mark.asyncio
async def test_resume_session_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_paused_session: dict,
    db: AsyncSession
):
    """Test resuming a paused session."""
    session_id = test_paused_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"

    # Verify in database
    session = await db.get(InterviewSession, uuid.UUID(session_id))
    await db.refresh(session)
    assert session.status == "active"

@pytest.mark.asyncio
async def test_pause_completed_session_fails(
    async_client: AsyncClient,
    test_user_token: str,
    test_completed_session: dict
):
    """Test cannot pause completed session."""
    session_id = test_completed_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/pause",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    assert "INVALID_SESSION_STATE" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_resume_active_session_fails(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict
):
    """Test cannot resume already active session."""
    session_id = test_active_session["id"]

    response = await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    assert "INVALID_SESSION_STATE" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_session_resume_workflow(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict
):
    """Test complete pause and resume workflow."""
    session_id = test_active_session["id"]

    # Pause session
    response1 = await async_client.put(
        f"/api/v1/sessions/{session_id}/pause",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    assert response1.json()["status"] == "paused"

    # Get session details (verify resume context available)
    response2 = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["status"] == "paused"
    assert "job_posting" in data
    assert "current_question_number" in data

    # Resume session
    response3 = await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response3.status_code == 200
    assert response3.json()["status"] == "active"

@pytest.mark.asyncio
async def test_resume_preserves_messages(
    async_client: AsyncClient,
    test_user_token: str,
    test_paused_session_with_messages: dict
):
    """Test resuming session preserves all messages."""
    session_id = test_paused_session_with_messages["id"]

    # Get messages before resume
    response1 = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    messages_before = response1.json()

    # Resume session
    await async_client.put(
        f"/api/v1/sessions/{session_id}/resume",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    # Get messages after resume
    response2 = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    messages_after = response2.json()

    # Verify messages unchanged
    assert len(messages_after) == len(messages_before)
    assert messages_after == messages_before
```

**Test Fixtures:**

```python
# backend/tests/conftest.py (add fixture)
@pytest.fixture
async def test_paused_session(
    db: AsyncSession,
    test_user: User,
    test_job_posting: JobPosting
):
    """Create a paused session."""
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="paused",
        current_question_number=2
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {"id": session.id}
```

### Dependencies

- Requires InterviewSession model from story 4.1
- Requires SessionResponse schema from story 4.2
- Requires session detail endpoint from story 4.4
- Requires messages endpoint from story 4.12

### Related Stories

- Story 4.1: Session model with status field
- Story 4.4: Session detail endpoint (provides resume context)
- Story 4.12: Messages endpoint (provides conversation history)
- Story 4.14: Session completion (final state transition)

### Frontend Resume Flow

1. User navigates to sessions list
2. Frontend calls GET /api/v1/sessions to get all sessions
3. User clicks on paused or active session
4. Frontend calls GET /api/v1/sessions/{id} to get full context
5. Frontend calls GET /api/v1/sessions/{id}/messages to load history
6. Frontend displays conversation UI with:
   - Job posting context
   - Current question number
   - All previous Q&A
   - "Continue" or "Resume" button
7. User can:
   - Submit answer if waiting for response
   - Request next question if ready
   - Pause session to return later

### Session State Persistence

**What persists automatically:**

- Session status (active/paused/completed)
- current_question_number (progress tracking)
- All SessionMessage records (Q&A history)
- Session metadata (created_at, updated_at)

**What frontend must reconstruct:**

- UI state (which input to show)
- Scroll position (optional UX enhancement)
- Pending operation polling (if interrupted during generation)

### Design Decisions

**Why explicit pause/resume endpoints?**

- Clear user intent (not just closing browser)
- Enables "Paused Sessions" list separate from active
- Future: Could auto-pause after inactivity timeout
- Explicit is better than implicit for state changes

**Why not auto-resume on access?**

- User might want to review before continuing
- Explicit resume shows user intent to continue
- Status distinction helps session management UI

**Why allow pausing during question generation?**

- User might need to leave urgently
- Can resume and check operation status later
- More flexible than forcing completion

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  State management patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR21, FR23-24 (resume, state tracking, persistence)

**Key Context Sections:**

- Session State: Status transitions, state machine
- API Patterns: PUT endpoints, idempotency
- Frontend Integration: State reconstruction from API

## Dev Agent Record

### Debug Log

- 2025-12-23: Added pause/resume endpoints, extended session detail resume
    context, and added tests; verified full backend suite green (347 tests).

### Completion Notes

- Task 1 complete: PUT `/api/v1/sessions/{id}/pause` enforces ownership (404)
  and state (400) and returns updated `SessionResponse`.
- Task 2 complete: PUT `/api/v1/sessions/{id}/resume` enforces ownership (404)
  and state (400) and returns updated `SessionResponse`.
- Task 3 complete: GET `/api/v1/sessions/{id}` includes `messages` in addition
    to session metadata, job posting, and resume.
- Frontend resume requirements: read `status` + `current_question_number`, and
    render from `messages` (also available via `/api/v1/sessions/{id}/messages`).
- Task 4 complete: added tests for pause/resume, invalid state, 404, 401, and
    session detail resume context.

## File List

- backend/app/api/v1/endpoints/sessions.py (modified)
- backend/app/schemas/session.py (modified)
- backend/app/services/session_service.py (modified)
- backend/tests/api/v1/test_sessions.py (added)
- \_bmad-output/implementation-artifacts/sprint-status.yaml (modified)
- \_bmad-output/implementation-artifacts/4-13-create-session-resume-capability.md
  (modified)

## Change Log

- 2025-12-23: Implemented session pause endpoint + initial integration tests;
  marked story in-progress in sprint-status.
- 2025-12-23: Implemented session resume endpoint + integration tests.
- 2025-12-23: Extended session detail response to include message history for
    resume.
