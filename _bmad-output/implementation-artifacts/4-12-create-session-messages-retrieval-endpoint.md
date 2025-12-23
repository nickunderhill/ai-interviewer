# Story 4.12: Create Session Messages Retrieval Endpoint

Status: done

## Story

As a user, I want to retrieve all messages (Q&A) for a session, so that I can
review the conversation history.

## Acceptance Criteria

1. **Given** I am authenticated and have a session **When** I GET
   `/api/v1/sessions/{id}/messages` **Then** the system validates I own the
   session **And** returns all SessionMessage records ordered by created_at ASC
   **And** each message includes: id, message_type, content, question_type (if
   applicable), created_at **And** returns 200 OK with array of messages **And**
   if the session doesn't exist or belongs to another user, returns 404 Not
   Found

## Tasks / Subtasks

- [x] Task 1: Implement messages retrieval service (AC: #1)

  - [x] Add get_session_messages function to
        `backend/app/services/session_service.py`
  - [x] Validate session exists and belongs to user
  - [x] Query SessionMessage filtered by session_id
  - [x] Order by created_at ASC (chronological conversation flow)
  - [x] Return list of SessionMessage objects
  - [x] Return 404 if session not found or unauthorized

- [x] Task 2: Create messages retrieval endpoint (AC: #1)

  - [x] Add GET /api/v1/sessions/{id}/messages to sessions.py router
  - [x] Use path parameter for session UUID
  - [x] Use get_current_user dependency for authentication
  - [x] Call session_service.get_session_messages
  - [x] Return 200 OK with list of MessageResponse
  - [x] Return empty array if no messages (not 404)
  - [x] Return 404 Not Found if session doesn't exist or unauthorized

- [x] Task 3: Add comprehensive tests (AC: #1)
  - [x] Add tests to `backend/tests/api/v1/test_sessions_get_messages.py`
  - [x] Test retrieves messages in chronological order
  - [x] Test questions and answers are both included
  - [x] Test message_type and question_type fields correct
  - [x] Test empty result returns empty array
  - [x] Test 404 for non-existent session
  - [x] Test 404 for other user's session
  - [x] Test 401 for unauthenticated request
  - [x] Test ordering (oldest first)

## Dev Agent Record

### File List

- backend/app/api/v1/endpoints/sessions.py
- backend/app/services/session_service.py
- backend/tests/api/v1/test_sessions_get_messages.py
- backend/tests/conftest.py
- backend/app/main.py
- backend/app/models/user.py
- backend/app/models/interview_session.py
- \_bmad-output/implementation-artifacts/sprint-status.yaml

### Change Log

- Implemented `GET /api/v1/sessions/{id}/messages` endpoint returning
  chronological session Q&A history.
- Added `get_session_messages` service method enforcing ownership (404 on
  missing/unauthorized) and ordering by `created_at ASC`.
- Added endpoint tests covering success, empty, unauthenticated (401), not found
  (404), and other-user (404).
- Stabilized async test environment to keep the full suite green.

## Senior Developer Review (AI)

Reviewer: Nick (AI-assisted) on 2025-12-23

- Updated story status/tasks to match implementation.
- Corrected test file path in documentation.
- Hardened hybrid client to reduce async DB event-loop mismatch risk.

## Dev Notes

### Critical Architecture Requirements

**API Patterns (STRICT):**

- Path: `/api/v1/sessions/{id}/messages` (nested under session)
- Method: GET (retrieval only)
- Response: 200 OK with array of messages
- Ordering: ASC by created_at (oldest first = conversation order)
- Empty result: Return `[]`, not 404

**Message Ordering:**

- Chronological order (created_at ASC) shows conversation flow
- Question → Answer → Question → Answer pattern
- Frontend displays in this order for natural reading
- Enables "scroll to bottom" for latest message

**Message Types:**

- Questions: message_type='question', question_type set
  (technical/behavioral/situational)
- Answers: message_type='answer', question_type=None
- Both types in same response array

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── api/v1/endpoints/
│   └── sessions.py              # UPDATE - Add messages endpoint
└── services/
    └── session_service.py       # UPDATE - Add get_session_messages
```

**Service Implementation:**

```python
# backend/app/services/session_service.py
from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.session_message import SessionMessage
from app.models.user import User

async def get_session_messages(
    db: AsyncSession,
    session_id: UUID,
    current_user: User
) -> List[SessionMessage]:
    """
    Get all messages for a session in chronological order.

    Args:
        db: Database session
        session_id: UUID of the session
        current_user: Authenticated user

    Returns:
        List of SessionMessage objects ordered by created_at ASC

    Raises:
        HTTPException: If session not found or unauthorized
    """
    # Validate session ownership
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

    # Get messages in chronological order
    result = await db.execute(
        select(SessionMessage)
        .where(SessionMessage.session_id == session_id)
        .order_by(SessionMessage.created_at.asc())
    )
    messages = result.scalars().all()

    return list(messages)
```

**Endpoint Implementation:**

```python
# backend/app/api/v1/endpoints/sessions.py
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.session import MessageResponse
from app.services import session_service

router = APIRouter()

@router.get(
    "/{session_id}/messages",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Get session messages (Q&A history)"
)
async def get_session_messages(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[MessageResponse]:
    """
    Get all messages (questions and answers) for a session.

    Messages are returned in chronological order (oldest first)
    to show the natural conversation flow.

    - **session_id**: UUID of the session
    - Returns questions and answers interleaved
    - Returns empty array if no messages yet
    - Returns 404 if session not found or unauthorized
    """
    messages = await session_service.get_session_messages(db, session_id, current_user)
    return [MessageResponse.model_validate(msg) for msg in messages]
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_get_messages_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_session_with_messages: dict
):
    """Test retrieving messages in chronological order."""
    session_id = test_session_with_messages["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) > 0

    # Verify chronological order
    timestamps = [msg["created_at"] for msg in data]
    assert timestamps == sorted(timestamps)

    # Verify message types
    for msg in data:
        assert msg["message_type"] in ["question", "answer"]
        if msg["message_type"] == "question":
            assert msg["question_type"] in ["technical", "behavioral", "situational"]
        else:
            assert msg["question_type"] is None

@pytest.mark.asyncio
async def test_get_messages_empty_session(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict
):
    """Test retrieving messages from session with no messages."""
    session_id = test_active_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_get_messages_alternating_types(
    async_client: AsyncClient,
    test_user_token: str,
    test_session_with_qa_pair: dict
):
    """Test messages show Q&A pattern."""
    session_id = test_session_with_qa_pair["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Assuming test fixture created Q, A, Q, A pattern
    assert len(data) >= 2

    # Find a question followed by answer
    for i in range(len(data) - 1):
        if data[i]["message_type"] == "question":
            # Next might be answer (not enforced, but typical pattern)
            assert "content" in data[i]

@pytest.mark.asyncio
async def test_get_messages_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test retrieving messages from non-existent session."""
    fake_id = uuid.uuid4()

    response = await async_client.get(
        f"/api/v1/sessions/{fake_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404
    assert "SESSION_NOT_FOUND" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_get_messages_other_user(
    async_client: AsyncClient,
    test_user_token: str,
    other_user_session: dict
):
    """Test cannot retrieve other user's messages."""
    session_id = other_user_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}/messages",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404  # Same as not found (security)

@pytest.mark.asyncio
async def test_get_messages_unauthorized(async_client: AsyncClient):
    """Test retrieving messages without authentication."""
    fake_id = uuid.uuid4()

    response = await async_client.get(f"/api/v1/sessions/{fake_id}/messages")

    assert response.status_code == 401
```

**Test Fixtures:**

```python
# backend/tests/conftest.py (add fixtures)
@pytest.fixture
async def test_session_with_messages(
    db: AsyncSession,
    test_user: User,
    test_job_posting: JobPosting
):
    """Create session with Q&A messages."""
    session = InterviewSession(
        user_id=test_user.id,
        job_posting_id=test_job_posting.id,
        status="active",
        current_question_number=2
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    # Add question
    question = SessionMessage(
        session_id=session.id,
        message_type="question",
        content="What is your experience with Python?",
        question_type="technical"
    )
    db.add(question)

    # Add answer
    answer = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content="I have 5 years of experience..."
    )
    db.add(answer)

    await db.commit()

    return {"id": session.id}
```

### Dependencies

- Requires SessionMessage model from story 4.1
- Requires InterviewSession model from story 4.1
- Requires MessageResponse schema from story 4.11
- Requires User authentication from Epic 2

### Related Stories

- Story 4.1: Created SessionMessage model
- Story 4.10: Stores questions (retrieved here)
- Story 4.11: Stores answers (retrieved here)
- Story 4.13: Resume capability (uses this endpoint)
- Frontend: Displays conversation history

### Performance Considerations

- Single query ordered by created_at
- Index on (session_id, created_at) from story 4.1 enables fast retrieval
- Typical session has < 20 messages (very fast)
- No pagination needed for MVP

### Frontend Integration

- Display messages in chronological order
- Alternate styling for questions vs answers
- Scroll to bottom for latest message
- Auto-refresh after submitting answer
- Show loading during question generation

### Design Decisions

**Why ASC order not DESC?**

- Natural conversation flow (top to bottom)
- Matches chat/messaging UX patterns
- Oldest messages at top, newest at bottom
- Frontend can reverse if needed

**Why empty array not 404?**

- Session exists but has no messages (valid state)
- RESTful convention: 404 for missing resource, 200 for empty collection
- New sessions start with no messages

**Why include questions and answers together?**

- Single request gets full conversation
- Simpler frontend (no separate endpoints)
- Chronological ordering requires both types together
- Future: Could filter by message_type if needed

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  List endpoints, ordering
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR35-36 (view previous answers, conversation history)

**Key Context Sections:**

- API Patterns: GET endpoints, list responses, empty arrays
- Database: Ordering queries, composite indexes
- Testing: Testing list endpoints with various states
