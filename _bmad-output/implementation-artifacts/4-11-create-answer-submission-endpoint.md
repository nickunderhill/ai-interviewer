# Story 4.11: Create Answer Submission Endpoint

Status: ready-for-dev

## Story

As a user, I want to submit my answer to an interview question, so that the
system records my response for future analysis.

## Acceptance Criteria

1. **Given** I am authenticated with an active session and a generated question
   **When** I POST to `/api/v1/sessions/{id}/answers` with `answer_text`
   **Then** the system validates I own the session **And** creates a
   SessionMessage record with message_type='answer' and content=answer_text
   **And** returns 201 Created with the message object **And** if the session is
   not active, returns 400 Bad Request

## Tasks / Subtasks

- [ ] Task 1: Create answer submission schemas (AC: #1)

  - [ ] Add AnswerCreate schema to `backend/app/schemas/session.py`
  - [ ] Include field: answer_text (str, required, non-empty)
  - [ ] Add MessageResponse schema for SessionMessage
  - [ ] Include all message fields (id, session_id, message_type, content,
        question_type, created_at)
  - [ ] Use Pydantic v2 validation

- [ ] Task 2: Implement answer submission service (AC: #1)

  - [ ] Add submit_answer function to `backend/app/services/session_service.py`
  - [ ] Validate session exists and belongs to user
  - [ ] Validate session status is 'active'
  - [ ] Create SessionMessage with message_type='answer'
  - [ ] Set content to answer_text
  - [ ] question_type is None for answers (only questions have types)
  - [ ] Return created SessionMessage

- [ ] Task 3: Create answer submission endpoint (AC: #1)

  - [ ] Add POST /api/v1/sessions/{id}/answers to sessions.py router
  - [ ] Use path parameter for session UUID
  - [ ] Use get_current_user dependency for authentication
  - [ ] Accept AnswerCreate schema in request body
  - [ ] Call session_service.submit_answer
  - [ ] Return 201 Created with MessageResponse
  - [ ] Return 400 Bad Request if session not active
  - [ ] Return 404 Not Found if session doesn't exist or unauthorized

- [ ] Task 4: Add comprehensive tests (AC: #1)
  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py`
  - [ ] Test successful answer submission returns 201
  - [ ] Test SessionMessage created with correct fields
  - [ ] Test answer validation (non-empty required)
  - [ ] Test 400 for non-active session
  - [ ] Test 404 for non-existent session
  - [ ] Test 404 for other user's session
  - [ ] Test 401 for unauthenticated request
  - [ ] Test multiple answers can be submitted

## Dev Notes

### Critical Architecture Requirements

**API Patterns (STRICT):**

- Path: `/api/v1/sessions/{id}/answers` (nested under session)
- Method: POST (creates new resource)
- Response: 201 Created with message object
- Validation: answer_text required, non-empty
- Session must be 'active' (not paused or completed)

**Database Patterns:**

- Create SessionMessage with message_type='answer'
- content field contains user's answer text
- question_type is None (only questions have types)
- Immediate persistence (FR34: save with timestamp immediately)
- No transaction complexity (single insert)

**Message Structure:**

- Questions have message_type='question' and question_type set
- Answers have message_type='answer' and question_type=None
- Both stored in same SessionMessage table
- Ordered by created_at for conversation flow

**Session State:**

- current_question_number doesn't change on answer submission
- Only increments when question is generated (story 4.10)
- Session status remains 'active' after answer
- User can submit multiple answers (corrections, follow-ups)

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── api/v1/endpoints/
│   └── sessions.py              # UPDATE - Add answers endpoint
├── schemas/
│   └── session.py               # UPDATE - Add AnswerCreate, MessageResponse
└── services/
    └── session_service.py       # UPDATE - Add submit_answer
```

**Answer Schemas:**

```python
# backend/app/schemas/session.py
from pydantic import BaseModel, ConfigDict, UUID4, Field
import datetime as dt
from typing import Optional

class AnswerCreate(BaseModel):
    """Request schema for submitting an answer."""
    answer_text: str = Field(..., min_length=1, description="User's answer text")

class MessageResponse(BaseModel):
    """Response schema for SessionMessage."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    session_id: UUID4
    message_type: str
    content: str
    question_type: Optional[str] = None
    created_at: dt.datetime
```

**Service Implementation:**

```python
# backend/app/services/session_service.py
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.session_message import SessionMessage
from app.models.user import User
from app.schemas.session import AnswerCreate

async def submit_answer(
    db: AsyncSession,
    session_id: UUID,
    answer_data: AnswerCreate,
    current_user: User
) -> SessionMessage:
    """
    Submit an answer to an interview session.

    Args:
        db: Database session
        session_id: UUID of the session
        answer_data: Answer content
        current_user: Authenticated user

    Returns:
        Created SessionMessage

    Raises:
        HTTPException: If session not found, unauthorized, or not active
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
                "code": "SESSION_NOT_ACTIVE",
                "message": f"Cannot submit answers to {session.status} session. Only active sessions accept answers."
            }
        )

    # Create answer message
    message = SessionMessage(
        session_id=session.id,
        message_type="answer",
        content=answer_data.answer_text,
        question_type=None  # Answers don't have question types
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message
```

**Endpoint Implementation:**

```python
# backend/app/api/v1/endpoints/sessions.py
from uuid import UUID
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.session import AnswerCreate, MessageResponse
from app.services import session_service

router = APIRouter()

@router.post(
    "/{session_id}/answers",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer to interview question"
)
async def submit_answer(
    session_id: UUID = Path(..., description="Session UUID"),
    answer_data: AnswerCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> MessageResponse:
    """
    Submit an answer to an interview question.

    - **session_id**: UUID of the active session
    - **answer_text**: User's answer (required, non-empty)
    - Returns 201 with message object
    - Returns 400 if session not active
    - Returns 404 if session not found or unauthorized
    """
    message = await session_service.submit_answer(db, session_id, answer_data, current_user)
    return MessageResponse.model_validate(message)
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.session_message import SessionMessage

@pytest.mark.asyncio
async def test_submit_answer_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict,
    db: AsyncSession
):
    """Test successful answer submission."""
    session_id = test_active_session["id"]
    answer_text = "I have 5 years of experience with Python, working on web applications using Django and FastAPI."

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"answer_text": answer_text}
    )

    assert response.status_code == 201
    data = response.json()

    assert data["message_type"] == "answer"
    assert data["content"] == answer_text
    assert data["question_type"] is None
    assert "created_at" in data

    # Verify message stored in database
    result = await db.execute(
        select(SessionMessage).where(
            SessionMessage.id == uuid.UUID(data["id"])
        )
    )
    message = result.scalar_one()
    assert message.content == answer_text

@pytest.mark.asyncio
async def test_submit_answer_empty_text(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict
):
    """Test answer submission with empty text."""
    session_id = test_active_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"answer_text": ""}
    )

    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_submit_answer_inactive_session(
    async_client: AsyncClient,
    test_user_token: str,
    test_completed_session: dict
):
    """Test cannot submit answer to completed session."""
    session_id = test_completed_session["id"]

    response = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"answer_text": "Test answer"}
    )

    assert response.status_code == 400
    assert "SESSION_NOT_ACTIVE" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_submit_answer_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test submitting answer to non-existent session."""
    fake_id = uuid.uuid4()

    response = await async_client.post(
        f"/api/v1/sessions/{fake_id}/answers",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"answer_text": "Test answer"}
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_submit_multiple_answers(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict,
    db: AsyncSession
):
    """Test submitting multiple answers to same session."""
    session_id = test_active_session["id"]

    # Submit first answer
    response1 = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"answer_text": "First answer"}
    )
    assert response1.status_code == 201

    # Submit second answer
    response2 = await async_client.post(
        f"/api/v1/sessions/{session_id}/answers",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"answer_text": "Second answer"}
    )
    assert response2.status_code == 201

    # Verify both stored
    result = await db.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == uuid.UUID(session_id),
            SessionMessage.message_type == "answer"
        )
    )
    answers = result.scalars().all()
    assert len(answers) == 2
```

### Dependencies

- Requires SessionMessage model from story 4.1
- Requires InterviewSession model from story 4.1
- Requires User authentication from Epic 2

### Related Stories

- Story 4.1: Created SessionMessage model
- Story 4.10: Stores questions (answers pair with questions)
- Story 4.12: Retrieves messages (reads questions and answers)
- Epic 5: Feedback analysis (analyzes submitted answers)

### Performance Considerations

- Single database insert (very fast)
- No complex queries or joins
- Index on session_id from story 4.1
- Answer text stored as Text (supports large answers)

### Security Considerations

- Session ownership validated
- Only active sessions accept answers
- Authentication required
- No rate limiting needed (natural human typing speed)

### Data Integrity

- Immediate persistence (FR34: save with timestamp)
- Answer linked to session via foreign key
- No orphaned answers (cascade delete with session)
- Timestamps are UTC

### User Experience

- Immediate response (< 100ms)
- User can submit multiple answers (corrections)
- User can see confirmation immediately
- No async pattern needed (simple insert)

### Design Decisions

**Why allow multiple answers?**

- User might want to correct answer
- User might submit follow-up thoughts
- Flexible conversation model
- Future: Could limit to one answer per question

**Why no question_id on answer?**

- Answer follows most recent question by time
- SessionMessage ordering (by created_at) maintains conversation flow
- Simpler data model (no question-answer pairing logic)
- Future: Could add question_id FK if needed

**Why 201 Created not 200 OK?**

- Creates new resource (SessionMessage)
- RESTful convention for POST that creates
- Location header could include message ID (future)

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  API patterns, validation
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR32-36 (answer submission, immediate save)

**Key Context Sections:**

- API Patterns: POST endpoints, 201 Created
- Validation: Pydantic Field validators
- Database: Simple inserts, timestamps
