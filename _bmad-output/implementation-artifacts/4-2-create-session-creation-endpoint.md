# Story 4.2: Create Session Creation Endpoint

Status: ready-for-dev

## Story

As a user, I want to start a new interview session for a job posting, so that I
can begin practicing interview questions.

## Acceptance Criteria

1. **Given** I am authenticated and have a job posting **When** I POST to
   `/api/v1/sessions` with `job_posting_id` **Then** the system validates I own
   the job posting **And** creates a new InterviewSession with status='active'
   and current_question_number=0 **And** returns 201 Created with the session
   object including id, job_posting_id, status, current_question_number,
   created_at **And** if the job posting doesn't exist or belongs to another
   user, returns 404 Not Found

## Tasks / Subtasks

- [ ] Task 1: Create Pydantic schemas for session creation (AC: #1)

  - [ ] Create `backend/app/schemas/session.py` with SessionCreate request
        schema
  - [ ] Include field: job_posting_id (UUID, required)
  - [ ] Create SessionResponse schema with all session fields
  - [ ] Include nested JobPosting schema (basic fields: id, title, company)
  - [ ] Use Pydantic v2 with ConfigDict for ORM mode

- [ ] Task 2: Implement session creation service (AC: #1)

  - [ ] Create `backend/app/services/session_service.py` with create_session
        function
  - [ ] Validate job posting exists using async query
  - [ ] Validate job posting belongs to authenticated user (user_id match)
  - [ ] Create InterviewSession with status='active', current_question_number=0
  - [ ] Return 404 if job posting not found or unauthorized
  - [ ] Use AsyncSession from SQLAlchemy 2.0+
  - [ ] Handle database exceptions gracefully

- [ ] Task 3: Create session creation API endpoint (AC: #1)

  - [ ] Create `backend/app/api/v1/endpoints/sessions.py` with POST
        /api/v1/sessions
  - [ ] Use get_current_user dependency for authentication
  - [ ] Accept SessionCreate schema in request body
  - [ ] Call session_service.create_session
  - [ ] Return 201 Created with SessionResponse
  - [ ] Return 404 Not Found with proper error detail if job posting invalid
  - [ ] Return 401 Unauthorized if not authenticated

- [ ] Task 4: Register endpoint in router (AC: #1)

  - [ ] Import sessions router in `backend/app/api/v1/api.py`
  - [ ] Register with prefix /sessions and tag "sessions"
  - [ ] Verify endpoint accessible at /api/v1/sessions

- [ ] Task 5: Add comprehensive tests (AC: #1)
  - [ ] Create `backend/tests/api/v1/test_sessions.py`
  - [ ] Test successful session creation returns 201 with correct fields
  - [ ] Test job_posting_id validation (non-existent posting returns 404)
  - [ ] Test ownership validation (other user's posting returns 404)
  - [ ] Test authentication requirement (no token returns 401)
  - [ ] Test default values (status='active', current_question_number=0)
  - [ ] Test database persistence (session saved correctly)
  - [ ] Mock database async operations correctly

## Dev Notes

### Critical Architecture Requirements

**API Patterns (STRICT):**

- Base path: `/api/v1/sessions`
- RESTful endpoint: `POST /api/v1/sessions` for creation
- Request body: JSON with Pydantic validation
- Response codes: 201 Created (success), 404 Not Found (invalid job posting),
  401 Unauthorized (not authenticated)
- Error format: `{"detail": {"code": "ERROR_CODE", "message": "description"}}`
- Authentication: JWT token in `Authorization: Bearer {token}` header

**Database Patterns:**

- Use async SQLAlchemy 2.0+ patterns (`AsyncSession`, `select()`)
- Query with explicit select: `await db.execute(select(JobPosting).where(...))`
- Validate ownership: Check `job_posting.user_id == current_user.id`
- Transaction boundaries: Service layer handles commit/rollback
- Never expose SQLAlchemy models to API - use Pydantic schemas

**Schema Patterns:**

- Request schemas: Suffix with `Create` (SessionCreate)
- Response schemas: Suffix with `Response` (SessionResponse)
- Use Pydantic v2 with `ConfigDict(from_attributes=True)` for ORM mode
- Nested schemas: Include related objects (job_posting details in session
  response)
- Field validation: Use Pydantic validators for UUIDs, required fields

**Service Layer:**

- Business logic isolated in services (not in endpoints)
- Services receive db session and authenticated user as parameters
- Services raise specific exceptions (HTTPException with status codes)
- Return Pydantic models, not ORM models

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── api/v1/endpoints/
│   └── sessions.py              # NEW - Session endpoints
├── schemas/
│   └── session.py               # NEW - Session Pydantic schemas
├── services/
│   └── session_service.py       # NEW - Session business logic
└── models/
    └── interview_session.py     # EXISTS (from 4.1)
```

**SessionCreate Schema:**

```python
# backend/app/schemas/session.py
from pydantic import BaseModel, UUID4

class SessionCreate(BaseModel):
    job_posting_id: UUID4
```

**SessionResponse Schema:**

```python
import datetime as dt
from typing import Optional
from pydantic import BaseModel, ConfigDict, UUID4

class JobPostingBasic(BaseModel):
    """Nested job posting info for session response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    company: Optional[str] = None

class SessionResponse(BaseModel):
    """Response schema for interview session."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    job_posting_id: Optional[UUID4] = None
    status: str
    current_question_number: int
    created_at: dt.datetime
    updated_at: dt.datetime
    job_posting: Optional[JobPostingBasic] = None
```

**Service Implementation Pattern:**

```python
# backend/app/services/session_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.user import User
from app.schemas.session import SessionCreate

async def create_session(
    db: AsyncSession,
    session_data: SessionCreate,
    current_user: User
) -> InterviewSession:
    """Create a new interview session."""

    # Fetch job posting with user validation
    result = await db.execute(
        select(JobPosting).where(
            JobPosting.id == session_data.job_posting_id,
            JobPosting.user_id == current_user.id
        )
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOB_POSTING_NOT_FOUND",
                "message": "Job posting not found or you don't have permission to access it"
            }
        )

    # Create session
    new_session = InterviewSession(
        user_id=current_user.id,
        job_posting_id=session_data.job_posting_id,
        status="active",
        current_question_number=0
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return new_session
```

**Endpoint Implementation Pattern:**

```python
# backend/app/api/v1/endpoints/sessions.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse
from app.services import session_service

router = APIRouter()

@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview session"
)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> SessionResponse:
    """
    Create a new interview session for a job posting.

    - **job_posting_id**: UUID of the job posting to practice for
    - Returns 201 with session details
    - Returns 404 if job posting not found or not owned by user
    """
    session = await session_service.create_session(db, session_data, current_user)
    return SessionResponse.model_validate(session)
```

**Router Registration:**

```python
# backend/app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import sessions

api_router = APIRouter()
api_router.include_router(
    sessions.router,
    prefix="/sessions",
    tags=["sessions"]
)
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_session_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_job_posting: dict
):
    """Test successful session creation."""
    response = await async_client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"job_posting_id": str(test_job_posting["id"])}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"
    assert data["current_question_number"] == 0
    assert data["job_posting_id"] == str(test_job_posting["id"])

@pytest.mark.asyncio
async def test_create_session_nonexistent_job_posting(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test session creation with non-existent job posting."""
    import uuid
    fake_id = str(uuid.uuid4())

    response = await async_client.post(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {test_user_token}"},
        json={"job_posting_id": fake_id}
    )

    assert response.status_code == 404
    assert "JOB_POSTING_NOT_FOUND" in response.json()["detail"]["code"]

@pytest.mark.asyncio
async def test_create_session_unauthorized(
    async_client: AsyncClient,
    test_job_posting: dict
):
    """Test session creation without authentication."""
    response = await async_client.post(
        "/api/v1/sessions",
        json={"job_posting_id": str(test_job_posting["id"])}
    )

    assert response.status_code == 401
```

### Dependencies

- Requires InterviewSession model from story 4.1
- Requires JobPosting model from Epic 3 (story 3.6)
- Requires User authentication from Epic 2 (get_current_user dependency)
- Requires get_db dependency from database setup (Epic 1)

### Related Stories

- Story 4.1: Created InterviewSession and SessionMessage models
- Story 4.3: Will list all sessions (uses same schemas)
- Story 4.4: Will retrieve session details (extends SessionResponse)
- Story 3.6-3.7: Job posting model and creation (prerequisite)

### Security Considerations

- Ownership validation prevents users from creating sessions for others' job
  postings
- Authentication enforced via JWT middleware
- No sensitive data exposed in error messages (generic "not found" for both
  non-existent and unauthorized)
- Foreign key relationships ensure referential integrity

### Performance Notes

- Single database query to validate job posting ownership
- Async operations prevent blocking
- Index on job_postings.user_id (from Epic 3) ensures fast ownership validation
- Session creation is lightweight (no complex processing)

### Error Handling

- 404 for non-existent or unauthorized job posting (security: same response for
  both)
- 401 for missing/invalid authentication token
- 500 for unexpected database errors (logged, not exposed to user)
- Validation errors return 422 with field-specific messages

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Complete implementation rules, patterns, and anti-patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  Technical constraints and architectural decisions
- Previous story: `4-1-create-session-and-message-models.md` - Model patterns
  established

**Key Context Sections:**

- Database & Backend Patterns: Naming conventions, SQLAlchemy 2.0+ async
  patterns
- API Patterns: RESTful conventions, error responses, authentication
- Testing Rules: pytest fixtures, mocking async operations
- Code Organization: Service layer vs API layer separation
