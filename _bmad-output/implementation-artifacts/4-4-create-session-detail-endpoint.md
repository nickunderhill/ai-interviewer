# Story 4.4: Create Session Detail Endpoint

Status: ready-for-dev

## Story

As a user, I want to view full details of a specific session, so that I can see
the context needed to resume or review an interview.

## Acceptance Criteria

1. **Given** I am authenticated and have a session **When** I GET
   `/api/v1/sessions/{id}` **Then** the system validates I own the session
   **And** returns the session with full job_posting details (title, company,
   description, tech_stack) and my resume content **And** returns 200 OK **And**
   if the session doesn't exist or belongs to another user, returns 404 Not
   Found

## Tasks / Subtasks

- [ ] Task 1: Extend session schemas for detailed response (AC: #1)

  - [ ] Create SessionDetailResponse in `backend/app/schemas/session.py`
  - [ ] Include complete JobPosting schema (all fields: title, company,
        description, experience_level, tech_stack)
  - [ ] Include Resume schema (content field)
  - [ ] Extend from SessionResponse or create complete schema
  - [ ] Use Pydantic v2 with nested models

- [ ] Task 2: Implement session detail service (AC: #1)

  - [ ] Add get_session_by_id function to
        `backend/app/services/session_service.py`
  - [ ] Query InterviewSession by id and user_id
  - [ ] Eager load job_posting relationship
  - [ ] Eager load user.resume relationship (for resume content)
  - [ ] Return 404 if session not found or belongs to another user
  - [ ] Handle case where resume might be None (user hasn't uploaded)

- [ ] Task 3: Create session detail API endpoint (AC: #1)

  - [ ] Add GET /api/v1/sessions/{id} endpoint to sessions.py router
  - [ ] Use path parameter for session UUID
  - [ ] Use get_current_user dependency for authentication
  - [ ] Call session_service.get_session_by_id
  - [ ] Return 200 OK with SessionDetailResponse
  - [ ] Return 404 if session not found or unauthorized

- [ ] Task 4: Add comprehensive tests (AC: #1)
  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py`
  - [ ] Test successful detail retrieval returns 200 with all fields
  - [ ] Test job_posting details are complete (description, tech_stack, etc.)
  - [ ] Test resume content is included
  - [ ] Test 404 for non-existent session
  - [ ] Test 404 for other user's session (ownership validation)
  - [ ] Test 401 for unauthenticated request
  - [ ] Test handles missing resume gracefully (resume=None)

## Dev Notes

### Critical Architecture Requirements

**API Patterns (STRICT):**

- Path: `/api/v1/sessions/{id}` with UUID path parameter
- Response codes: 200 OK (success), 404 Not Found (not found or unauthorized),
  401 Unauthorized
- Security: Same 404 response for non-existent and unauthorized (prevent
  information disclosure)
- Complete data: Include full job_posting and resume in response

**Database Patterns:**

- Eager loading: Load job_posting AND user.resume to prevent N+1
- Use `selectinload()` or `joinedload()` for relationships
- Query pattern: Filter by both id AND user_id for security
- Handle nullable resume (user might not have uploaded yet)

**Schema Patterns:**

- Nested models: JobPostingDetail, ResumeDetail in SessionDetailResponse
- Optional fields: resume might be None
- Reuse existing schemas where possible (DRY principle)

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── api/v1/endpoints/
│   └── sessions.py              # UPDATE - Add GET /{id}
├── schemas/
│   ├── session.py               # UPDATE - Add SessionDetailResponse
│   ├── job_posting.py           # Reference existing JobPostingResponse
│   └── resume.py                # Reference existing ResumeResponse
└── services/
    └── session_service.py       # UPDATE - Add get_session_by_id
```

**SessionDetailResponse Schema:**

```python
# backend/app/schemas/session.py
from typing import Optional
from pydantic import BaseModel, ConfigDict, UUID4
import datetime as dt

# Import existing schemas
from app.schemas.job_posting import JobPostingResponse
from app.schemas.resume import ResumeResponse

class SessionDetailResponse(BaseModel):
    """Detailed session response including full job posting and resume."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    job_posting_id: Optional[UUID4] = None
    status: str
    current_question_number: int
    created_at: dt.datetime
    updated_at: dt.datetime

    # Full related objects
    job_posting: Optional[JobPostingResponse] = None
    resume: Optional[ResumeResponse] = None  # From user relationship
```

**Service Implementation Pattern:**

```python
# backend/app/services/session_service.py
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.user import User

async def get_session_by_id(
    db: AsyncSession,
    session_id: UUID,
    current_user: User
) -> InterviewSession:
    """Get a session by ID with full details."""

    # Query with eager loading for job_posting and resume
    result = await db.execute(
        select(InterviewSession)
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id
        )
        .options(
            selectinload(InterviewSession.job_posting),
            selectinload(InterviewSession.user).selectinload(User.resume)
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

    return session
```

**Endpoint Implementation Pattern:**

```python
# backend/app/api/v1/endpoints/sessions.py
from uuid import UUID
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.session import SessionDetailResponse
from app.services import session_service

router = APIRouter()

@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get session details"
)
async def get_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionDetailResponse:
    """
    Get full details of a specific interview session.

    - **session_id**: UUID of the session
    - Returns full session with job posting details and resume content
    - Returns 404 if not found or unauthorized
    """
    session = await session_service.get_session_by_id(db, session_id, current_user)
    return SessionDetailResponse.model_validate(session)
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient
import uuid

@pytest.mark.asyncio
async def test_get_session_detail_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_session_full: dict  # Session with job posting and resume
):
    """Test retrieving full session details."""
    session_id = test_session_full["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify all fields present
    assert data["id"] == str(session_id)
    assert data["status"] in ["active", "paused", "completed"]

    # Verify job posting details
    assert "job_posting" in data
    assert data["job_posting"]["title"] is not None
    assert data["job_posting"]["description"] is not None

    # Verify resume content
    assert "resume" in data
    if data["resume"]:
        assert "content" in data["resume"]

@pytest.mark.asyncio
async def test_get_session_detail_not_found(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test retrieving non-existent session."""
    fake_id = uuid.uuid4()

    response = await async_client.get(
        f"/api/v1/sessions/{fake_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404
    assert "SESSION_NOT_FOUND" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_get_session_detail_other_user(
    async_client: AsyncClient,
    test_user_token: str,
    other_user_session: dict  # Session owned by different user
):
    """Test retrieving another user's session."""
    session_id = other_user_session["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 404  # Security: same as not found

@pytest.mark.asyncio
async def test_get_session_detail_without_resume(
    async_client: AsyncClient,
    test_user_token: str,
    test_session_no_resume: dict
):
    """Test session detail when user hasn't uploaded resume."""
    session_id = test_session_no_resume["id"]

    response = await async_client.get(
        f"/api/v1/sessions/{session_id}",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["resume"] is None  # Gracefully handles missing resume
```

### Dependencies

- Requires InterviewSession model from story 4.1
- Requires SessionResponse schema from story 4.2
- Requires JobPostingResponse schema from Epic 3
- Requires ResumeResponse schema from Epic 3
- Requires User model with resume relationship from Epic 2/3

### Related Stories

- Story 4.1: Created InterviewSession model
- Story 4.2-4.3: Created basic session endpoints
- Story 4.13: Session resume capability (uses this endpoint)
- Epic 3 stories: Job posting and resume models/schemas

### Performance Considerations

- **Eager Loading:** Use selectinload for both job_posting and user.resume
- **Single Query:** Load all related data in one query to prevent N+1
- **Index Usage:** Benefits from PK index on sessions and FKs on relationships
- **Resume Size:** Resume content can be large (text field), acceptable for
  detail view

### Security Considerations

- Ownership validated by filtering on both id AND user_id
- Same 404 response for non-existent and unauthorized (prevents enumeration)
- Authentication required via JWT middleware
- No sensitive data exposure (user's own data only)

### Frontend Integration Notes

- Used for "Resume Session" functionality (story 4.13)
- Provides all context needed to reconstruct session UI
- Includes resume and job posting so frontend doesn't need additional calls
- Handles missing resume gracefully (user might not have uploaded)

### Error Handling

- 404 for session not found or unauthorized (security: same message)
- 401 for missing/invalid authentication
- 422 for invalid UUID format in path parameter
- 500 for database errors (logged, not exposed)

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Nested schema patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  Security requirements

**Key Context Sections:**

- Schema Patterns: Nested models, optional fields
- Database Patterns: Eager loading multiple relationships
- Security: Ownership validation, same error for not found/unauthorized
