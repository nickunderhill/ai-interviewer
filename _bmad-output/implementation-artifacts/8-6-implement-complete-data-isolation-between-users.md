# Story 8.6: Implement Complete Data Isolation Between Users

Status: ready-for-dev

## Story

As a developer, I want to ensure strict data isolation between users, so that no
user can access another user's data.

## Acceptance Criteria

1. **Given** all API endpoints are implemented **When** any endpoint is called
   **Then** it uses the `get_current_user` dependency to identify the
   authenticated user **And** all database queries filter by user_id (or related
   user_id via foreign keys) **And** authorization checks validate ownership
   before any read/update/delete operation **And** the system returns 404 Not
   Found (not 403) for unauthorized access to hide resource existence **And**
   SQL queries never allow cross-user data leakage **And** integration tests
   verify data isolation for all endpoints **And** follows OWASP principle of
   least privilege (NFR3, NFR10, FR63) ✅

## Tasks / Subtasks

- [ ] Task 1: Audit all API endpoints for user isolation (AC: #1)

  - [ ] List all endpoints in `backend/app/api/v1/endpoints/`
  - [ ] Verify each protected endpoint uses `get_current_user` dependency
  - [ ] Check database queries filter by user_id
  - [ ] Identify endpoints that need authorization checks

- [ ] Task 2: Implement authorization helper functions (AC: #1)

  - [ ] Create `backend/app/core/authorization.py`
  - [ ] Add `verify_session_ownership(session_id, user_id, db)`
  - [ ] Add `verify_job_posting_ownership(job_id, user_id, db)`
  - [ ] Add `verify_resume_ownership(resume_id, user_id, db)`
  - [ ] Return 404 for unauthorized access (not 403)

- [ ] Task 3: Update session endpoints with authorization (AC: #1)

  - [ ] GET `/api/v1/sessions/{id}` - verify ownership
  - [ ] PUT `/api/v1/sessions/{id}` - verify ownership
  - [ ] DELETE `/api/v1/sessions/{id}` - verify ownership
  - [ ] GET `/api/v1/sessions` - filter by current_user.id
  - [ ] POST `/api/v1/sessions/{id}/messages` - verify session ownership

- [ ] Task 4: Update job posting endpoints with authorization (AC: #1)

  - [ ] GET `/api/v1/job-postings/{id}` - verify ownership
  - [ ] PUT `/api/v1/job-postings/{id}` - verify ownership
  - [ ] DELETE `/api/v1/job-postings/{id}` - verify ownership
  - [ ] GET `/api/v1/job-postings` - filter by current_user.id

- [ ] Task 5: Update resume endpoints with authorization (AC: #1)

  - [ ] GET `/api/v1/resumes/{id}` - verify ownership
  - [ ] PUT `/api/v1/resumes/{id}` - verify ownership
  - [ ] DELETE `/api/v1/resumes/{id}` - verify ownership
  - [ ] GET `/api/v1/resumes` - filter by current_user.id

- [ ] Task 6: Update feedback and operation endpoints (AC: #1)

  - [ ] GET `/api/v1/feedback/{id}` - verify via session ownership
  - [ ] GET `/api/v1/operations/{id}` - verify via session ownership
  - [ ] Ensure all nested resources check parent ownership

- [ ] Task 7: Write integration tests for data isolation (AC: #1)
  - [ ] Create test with 2 users
  - [ ] Verify User A cannot access User B's sessions
  - [ ] Verify User A cannot access User B's job postings
  - [ ] Verify User A cannot access User B's resumes
  - [ ] Verify 404 responses (not 403) for unauthorized access
  - [ ] Test all CRUD operations for isolation

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Authentication:** All protected endpoints use `get_current_user` dependency
- **Authorization:** Ownership verification before data access
- **Error Handling:** 404 for unauthorized access (security through obscurity)
- **SQL Queries:** Always filter by user_id or related foreign keys
- **Testing:** Integration tests for all data isolation scenarios

**Security Principles:**

- OWASP Principle of Least Privilege
- Defense in depth (authentication + authorization)
- Secure by default (deny unless explicitly allowed)
- No data leakage through error messages

### File Structure

```
backend/app/
├── core/
│   └── authorization.py       # Authorization helper functions
├── api/v1/endpoints/
│   ├── sessions.py            # Update with authorization checks
│   ├── job_postings.py        # Update with authorization checks
│   ├── resumes.py             # Update with authorization checks
│   ├── feedback.py            # Update with authorization checks
│   └── operations.py          # Update with authorization checks
└── tests/
    └── integration/
        └── test_data_isolation.py  # Comprehensive isolation tests
```

### Implementation Details

**Authorization Helpers:**

```python
# backend/app/core/authorization.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.resume import Resume
import logging

logger = logging.getLogger(__name__)

async def verify_session_ownership(
    session_id: str,
    user_id: str,
    db: AsyncSession
) -> InterviewSession:
    """
    Verify user owns the session.

    Returns session if authorized, raises 404 if not found or unauthorized.
    """
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .where(InterviewSession.user_id == user_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        # Return 404 instead of 403 to hide resource existence
        logger.warning(f"Unauthorized session access attempt", extra={
            "session_id": session_id,
            "user_id": user_id
        })
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session

async def verify_job_posting_ownership(
    job_posting_id: str,
    user_id: str,
    db: AsyncSession
) -> JobPosting:
    """
    Verify user owns the job posting.

    Returns job posting if authorized, raises 404 if not found or unauthorized.
    """
    result = await db.execute(
        select(JobPosting)
        .where(JobPosting.id == job_posting_id)
        .where(JobPosting.user_id == user_id)
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        logger.warning(f"Unauthorized job posting access attempt", extra={
            "job_posting_id": job_posting_id,
            "user_id": user_id
        })
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job posting not found"
        )

    return job_posting

async def verify_resume_ownership(
    resume_id: str,
    user_id: str,
    db: AsyncSession
) -> Resume:
    """
    Verify user owns the resume.

    Returns resume if authorized, raises 404 if not found or unauthorized.
    """
    result = await db.execute(
        select(Resume)
        .where(Resume.id == resume_id)
        .where(Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()

    if not resume:
        logger.warning(f"Unauthorized resume access attempt", extra={
            "resume_id": resume_id,
            "user_id": user_id
        })
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    return resume

async def verify_operation_ownership(
    operation_id: str,
    user_id: str,
    db: AsyncSession
) -> Operation:
    """
    Verify user owns the operation (via session ownership).
    """
    from app.models.operation import Operation

    result = await db.execute(
        select(Operation)
        .join(InterviewSession)
        .where(Operation.id == operation_id)
        .where(InterviewSession.user_id == user_id)
    )
    operation = result.scalar_one_or_none()

    if not operation:
        logger.warning(f"Unauthorized operation access attempt", extra={
            "operation_id": operation_id,
            "user_id": user_id
        })
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operation not found"
        )

    return operation
```

**Updated Session Endpoints:**

```python
# backend/app/api/v1/endpoints/sessions.py (update)
from app.core.authorization import verify_session_ownership

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get session details with authorization check."""
    session = await verify_session_ownership(session_id, current_user.id, db)
    return session

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update session with authorization check."""
    session = await verify_session_ownership(session_id, current_user.id, db)

    # Apply updates
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(session, key, value)

    await db.commit()
    await db.refresh(session)
    return session

@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete session with authorization check."""
    session = await verify_session_ownership(session_id, current_user.id, db)

    await db.delete(session)
    await db.commit()
    return {"message": "Session deleted successfully"}

@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List sessions filtered by current user."""
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(InterviewSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return sessions
```

**Integration Tests:**

```python
# backend/tests/integration/test_data_isolation.py
import pytest
from httpx import AsyncClient
from app.models.user import User
from app.models.session import InterviewSession

@pytest.mark.asyncio
async def test_user_cannot_access_other_user_session(
    client: AsyncClient,
    db: AsyncSession,
    test_user_1: User,
    test_user_2: User,
    user_1_token: str,
    user_2_token: str
):
    """Test that User 1 cannot access User 2's session."""
    # Create session for User 2
    session = InterviewSession(
        user_id=test_user_2.id,
        job_posting_id=test_user_2_job.id,
        status="active"
    )
    db.add(session)
    await db.commit()

    # User 1 tries to access User 2's session
    response = await client.get(
        f"/api/v1/sessions/{session.id}",
        headers={"Authorization": f"Bearer {user_1_token}"}
    )

    # Should return 404, not 403
    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found"

@pytest.mark.asyncio
async def test_user_cannot_update_other_user_session(
    client: AsyncClient,
    db: AsyncSession,
    test_user_1: User,
    test_user_2: User,
    user_1_token: str,
    user_2_session: InterviewSession
):
    """Test that User 1 cannot update User 2's session."""
    response = await client.put(
        f"/api/v1/sessions/{user_2_session.id}",
        json={"status": "completed"},
        headers={"Authorization": f"Bearer {user_1_token}"}
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_cannot_delete_other_user_session(
    client: AsyncClient,
    test_user_1: User,
    test_user_2: User,
    user_1_token: str,
    user_2_session: InterviewSession
):
    """Test that User 1 cannot delete User 2's session."""
    response = await client.delete(
        f"/api/v1/sessions/{user_2_session.id}",
        headers={"Authorization": f"Bearer {user_1_token}"}
    )

    assert response.status_code == 404

@pytest.mark.asyncio
async def test_user_cannot_list_other_user_sessions(
    client: AsyncClient,
    test_user_1: User,
    test_user_2: User,
    user_1_token: str,
    user_1_sessions: List[InterviewSession],
    user_2_sessions: List[InterviewSession]
):
    """Test that User 1 only sees their own sessions."""
    response = await client.get(
        "/api/v1/sessions",
        headers={"Authorization": f"Bearer {user_1_token}"}
    )

    assert response.status_code == 200
    sessions = response.json()

    # User 1 should only see their own sessions
    session_ids = [s["id"] for s in sessions]
    for user_1_session in user_1_sessions:
        assert str(user_1_session.id) in session_ids
    for user_2_session in user_2_sessions:
        assert str(user_2_session.id) not in session_ids

# Similar tests for job postings, resumes, feedback, operations
```

### Testing Requirements

**Test Coverage:**

- All endpoints verify user ownership
- Unauthorized access returns 404 (not 403)
- List endpoints filter by user_id
- No cross-user data leakage
- SQL queries always filter by user_id
- Integration tests for all resource types

**Test Files:**

- `backend/tests/integration/test_data_isolation.py`
- `backend/tests/core/test_authorization.py`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.6]
- [NFR3, NFR10: Security requirements]
- [FR63: Ensure users only access their own data]
- [OWASP: Principle of Least Privilege]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with comprehensive data isolation
- Authorization helpers for all resource types
- 404 responses for unauthorized access
- Integration tests for data isolation
- Ready for dev implementation
