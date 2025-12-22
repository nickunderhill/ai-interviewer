# Story 4.3: Create Session List Endpoint

Status: ready-for-dev

## Story

As a user, I want to view my interview sessions, so that I can see sessions
grouped by status (active/paused/completed).

## Acceptance Criteria

1. **Given** I am authenticated **When** I GET `/api/v1/sessions` **Then** the
   system returns all my sessions ordered by created_at DESC **And** supports
   optional query parameter `status` to filter (active/paused/completed) **And**
   each session includes: id, job_posting (with title, company), status,
   current_question_number, created_at **And** returns 200 OK with array of
   sessions

## Tasks / Subtasks

- [ ] Task 1: Extend session schemas for list response (AC: #1)

  - [ ] Update `backend/app/schemas/session.py` with SessionListResponse
  - [ ] Include job_posting nested object (title, company, id)
  - [ ] Reuse SessionResponse schema or create specialized list item schema
  - [ ] Ensure consistent field naming and types

- [ ] Task 2: Implement session listing service (AC: #1)

  - [ ] Add get_sessions_by_user function to
        `backend/app/services/session_service.py`
  - [ ] Accept optional status filter parameter
  - [ ] Query InterviewSession filtered by user_id
  - [ ] Apply status filter if provided (validate against valid statuses)
  - [ ] Order by created_at DESC (newest first)
  - [ ] Use eager loading for job_posting relationship (joinedload or
        selectinload)
  - [ ] Return list of sessions

- [ ] Task 3: Create session list API endpoint (AC: #1)

  - [ ] Add GET /api/v1/sessions endpoint to sessions.py router
  - [ ] Use get_current_user dependency for authentication
  - [ ] Accept optional query parameter: status (str, optional)
  - [ ] Validate status parameter if provided (active/paused/completed)
  - [ ] Call session_service.get_sessions_by_user
  - [ ] Return 200 OK with list of SessionListResponse
  - [ ] Return empty array if no sessions found (not 404)

- [ ] Task 4: Add comprehensive tests (AC: #1)
  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py`
  - [ ] Test list all sessions returns 200 with correct ordering
  - [ ] Test status filter returns only matching sessions
  - [ ] Test empty result returns empty array (not error)
  - [ ] Test authentication requirement (no token returns 401)
  - [ ] Test user isolation (only returns current user's sessions)
  - [ ] Test job_posting data is included and correct
  - [ ] Test ordering is correct (newest first)

## Dev Notes

### Critical Architecture Requirements

**API Patterns (STRICT):**

- Base path: `/api/v1/sessions`
- RESTful endpoint: `GET /api/v1/sessions` for listing
- Query parameters: `?status=active` (optional filter)
- Response codes: 200 OK (success, even if empty), 401 Unauthorized (not
  authenticated)
- Empty results: Return `[]`, not 404
- Ordering: Always DESC by created_at (newest first)

**Database Patterns:**

- Use async SQLAlchemy 2.0+ with select() construct
- Eager loading: Use `selectinload(InterviewSession.job_posting)` to avoid N+1
  queries
- Filtering: Apply where() clause for user_id and optional status
- Ordering: `.order_by(InterviewSession.created_at.desc())`
- User isolation: Always filter by current_user.id

**Query Optimization:**

- Eager load job_posting relationship to prevent N+1 queries
- Use index on user_id + created_at (from story 4.1)
- Limit results if pagination needed in future (not MVP requirement)

### Technical Implementation Details

**File Structure:**

```
backend/app/
├── api/v1/endpoints/
│   └── sessions.py              # UPDATE - Add GET endpoint
├── schemas/
│   └── session.py               # UPDATE - Add list schemas if needed
└── services/
    └── session_service.py       # UPDATE - Add get_sessions_by_user
```

**Service Implementation Pattern:**

```python
# backend/app/services/session_service.py
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.interview_session import InterviewSession
from app.models.user import User

async def get_sessions_by_user(
    db: AsyncSession,
    current_user: User,
    status_filter: Optional[str] = None
) -> List[InterviewSession]:
    """Get all sessions for a user, optionally filtered by status."""

    # Validate status if provided
    if status_filter and status_filter not in ["active", "paused", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_FILTER",
                "message": f"Invalid status filter. Must be one of: active, paused, completed"
            }
        )

    # Build query with eager loading
    query = select(InterviewSession).where(
        InterviewSession.user_id == current_user.id
    ).options(
        selectinload(InterviewSession.job_posting)
    )

    # Apply status filter if provided
    if status_filter:
        query = query.where(InterviewSession.status == status_filter)

    # Order by newest first
    query = query.order_by(InterviewSession.created_at.desc())

    result = await db.execute(query)
    sessions = result.scalars().all()

    return list(sessions)
```

**Endpoint Implementation Pattern:**

```python
# backend/app/api/v1/endpoints/sessions.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.session import SessionResponse
from app.services import session_service

router = APIRouter()

@router.get(
    "",
    response_model=List[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List user's interview sessions"
)
async def list_sessions(
    status: Optional[str] = Query(None, description="Filter by status: active, paused, or completed"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[SessionResponse]:
    """
    Get all interview sessions for the authenticated user.

    - **status**: Optional filter by session status
    - Returns sessions ordered by created_at DESC (newest first)
    - Returns empty array if no sessions found
    """
    sessions = await session_service.get_sessions_by_user(db, current_user, status)
    return [SessionResponse.model_validate(session) for session in sessions]
```

**Testing Patterns:**

```python
# backend/tests/api/v1/test_sessions.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_sessions_success(
    async_client: AsyncClient,
    test_user_token: str,
    test_sessions: list  # Fixture creating multiple sessions
):
    """Test listing all sessions."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify ordering (newest first)
    dates = [session["created_at"] for session in data]
    assert dates == sorted(dates, reverse=True)

@pytest.mark.asyncio
async def test_list_sessions_with_status_filter(
    async_client: AsyncClient,
    test_user_token: str,
    test_active_session: dict,
    test_completed_session: dict
):
    """Test filtering sessions by status."""
    response = await async_client.get(
        "/api/v1/sessions?status=active",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert all(session["status"] == "active" for session in data)

@pytest.mark.asyncio
async def test_list_sessions_empty_result(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test listing sessions when user has none."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_list_sessions_includes_job_posting(
    async_client: AsyncClient,
    test_user_token: str,
    test_session_with_job_posting: dict
):
    """Test that job posting details are included."""
    response = await async_client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    session = data[0]
    assert "job_posting" in session
    assert session["job_posting"]["title"] is not None

@pytest.mark.asyncio
async def test_list_sessions_unauthorized(async_client: AsyncClient):
    """Test listing sessions without authentication."""
    response = await async_client.get("/api/v1/sessions")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_sessions_invalid_status_filter(
    async_client: AsyncClient,
    test_user_token: str
):
    """Test invalid status filter."""
    response = await async_client.get(
        "/api/v1/sessions?status=invalid",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )

    assert response.status_code == 400
    assert "INVALID_STATUS_FILTER" in response.json()["detail"]["code"]
```

**Test Fixtures:**

```python
# backend/tests/conftest.py (add fixtures)
@pytest.fixture
async def test_sessions(db: AsyncSession, test_user: User, test_job_posting: JobPosting):
    """Create multiple test sessions with different statuses."""
    sessions = []
    for status in ["active", "paused", "completed"]:
        session = InterviewSession(
            user_id=test_user.id,
            job_posting_id=test_job_posting.id,
            status=status,
            current_question_number=0
        )
        db.add(session)
        sessions.append(session)

    await db.commit()
    for session in sessions:
        await db.refresh(session)

    return sessions
```

### Dependencies

- Requires InterviewSession model from story 4.1
- Requires SessionResponse schema from story 4.2
- Requires User authentication from Epic 2 (get_current_user)
- Requires JobPosting model from Epic 3 for relationship loading

### Related Stories

- Story 4.1: Created InterviewSession model with indexes
- Story 4.2: Created SessionResponse schema (reused here)
- Story 4.4: Will extend with full session details
- Story 6.1-6.7: Session history and filtering (extends this endpoint)

### Performance Considerations

- **N+1 Query Prevention:** Use `selectinload(InterviewSession.job_posting)` to
  eagerly load relationships
- **Index Usage:** Query benefits from composite index on (user_id, created_at)
  from story 4.1
- **Pagination:** Not required for MVP (typical user has < 100 sessions)
- **Async Execution:** Non-blocking database queries

### Security Considerations

- User isolation enforced via user_id filter (users only see their own sessions)
- Authentication required for all requests
- No sensitive data in job_posting nested object (only id, title, company)
- Status filter validated to prevent SQL injection

### Error Handling

- 200 with empty array for no results (RESTful best practice)
- 400 for invalid status filter value
- 401 for missing/invalid authentication
- 500 for database errors (logged, not exposed)

### Frontend Integration Notes

- Frontend can call without status filter to get all sessions
- Frontend can filter by status for "Active Sessions" vs "Completed Sessions"
  tabs
- Job posting data included to display session context without additional API
  calls
- Ordering (newest first) matches expected UX pattern

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Complete implementation rules
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  Performance requirements (NFR-P1)

**Key Context Sections:**

- API Patterns: List endpoints, query parameters, empty results
- Database Patterns: Eager loading, N+1 prevention, ordering
- Performance: Query optimization, index usage
