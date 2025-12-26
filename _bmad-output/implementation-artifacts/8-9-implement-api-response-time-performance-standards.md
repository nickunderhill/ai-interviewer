# Story 8.9: Implement API Response Time Performance Standards

Status: ready-for-dev

## Story

As a developer, I want to ensure all API endpoints meet performance
requirements, so that the user experience is responsive.

## Acceptance Criteria

1. **Given** all API endpoints are implemented **When** measuring response times
   under normal load **Then** GET endpoints (sessions list, session detail,
   feedback retrieval, messages) respond in <300ms **And** POST endpoints
   (session creation, answer submission) respond in <500ms **And** Database
   queries use proper indexes on foreign keys (user_id, session_id,
   job_posting_id) **And** Eager loading (joinedload) is used to avoid N+1
   queries **And** Async database operations (SQLAlchemy async) are used
   throughout **And** performance tests validate these thresholds **And** slow
   queries are logged for optimization (NFR1, NFR16) ✅

## Tasks / Subtasks

- [ ] Task 1: Identify critical endpoints and baseline performance (AC: #1)

  - [ ] List endpoints: sessions list/detail, messages list, feedback retrieval
  - [ ] Measure baseline response times locally
  - [ ] Identify slow endpoints (>300ms GET, >500ms POST)
  - [ ] Profile database queries for each endpoint

- [ ] Task 2: Add/verify database indexes (AC: #1)

  - [ ] Ensure indexes exist for: users.id, sessions.user_id
  - [ ] Add indexes for: session_messages.session_id
  - [ ] Add indexes for: feedback.message_id/session_id
  - [ ] Add indexes for: job_postings.user_id
  - [ ] Add indexes for: operations.session_id
  - [ ] Create Alembic migration for any missing indexes

- [ ] Task 3: Fix N+1 queries with eager loading (AC: #1)

  - [ ] Audit SQLAlchemy queries using relationships
  - [ ] Add joinedload/selectinload where appropriate
  - [ ] Ensure session detail loads messages efficiently
  - [ ] Ensure history list loads aggregated fields efficiently
  - [ ] Avoid loading large text blobs unnecessarily

- [ ] Task 4: Ensure async DB usage throughout (AC: #1)

  - [ ] Verify all endpoints use AsyncSession
  - [ ] Ensure services use async SQLAlchemy patterns
  - [ ] Remove any blocking calls in request handlers

- [ ] Task 5: Add slow query logging (AC: #1)

  - [ ] Log queries slower than 200ms
  - [ ] Include endpoint name and query duration
  - [ ] Add structured logging fields
  - [ ] Ensure sensitive data not logged

- [ ] Task 6: Create performance tests (AC: #1)
  - [ ] Add pytest benchmarks or simple timing tests
  - [ ] Test critical GET endpoints under seeded data
  - [ ] Validate thresholds (<300ms, <500ms)
  - [ ] Fail tests if thresholds exceeded

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Async:** SQLAlchemy 2.0 async everywhere
- **Indexes:** Foreign keys and frequently filtered columns indexed
- **Eager Loading:** Use joinedload/selectinload to avoid N+1
- **Logging:** Slow query logging for optimization
- **Testing:** Performance tests to validate thresholds

### File Structure

```
backend/app/
├── core/
│   └── database.py            # Async engine/session config
├── api/v1/endpoints/
│   ├── sessions.py            # Optimize queries
│   ├── messages.py            # Optimize queries
│   └── feedback.py            # Optimize queries
├── utils/
│   └── performance.py         # Timing utilities and slow query logging
└── alembic/versions/
    └── xxxx_add_performance_indexes.py

backend/tests/
└── performance/
    └── test_api_performance.py
```

### Implementation Details

**Adding Indexes (SQLAlchemy Model Example):**

```python
# backend/app/models/session.py
from sqlalchemy import Index

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    # ... fields ...
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

# Add index
Index("ix_interview_sessions_user_id", InterviewSession.user_id)
```

**Alembic Migration for Indexes:**

```python
# backend/alembic/versions/xxxx_add_performance_indexes.py
from alembic import op

def upgrade():
    op.create_index(
        'ix_session_messages_session_id',
        'session_messages',
        ['session_id']
    )
    op.create_index(
        'ix_job_postings_user_id',
        'job_postings',
        ['user_id']
    )
    op.create_index(
        'ix_operations_session_id',
        'operations',
        ['session_id']
    )

def downgrade():
    op.drop_index('ix_session_messages_session_id')
    op.drop_index('ix_job_postings_user_id')
    op.drop_index('ix_operations_session_id')
```

**Eager Loading Example:**

```python
# backend/app/api/v1/endpoints/sessions.py
from sqlalchemy.orm import selectinload

@router.get("/{session_id}")
async def get_session_detail(session_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(InterviewSession)
        .options(
            selectinload(InterviewSession.messages),
            selectinload(InterviewSession.job_posting),
        )
        .where(InterviewSession.id == session_id)
        .where(InterviewSession.user_id == current_user.id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
```

**Slow Query Logging:**

```python
# backend/app/utils/performance.py
import time
import logging

logger = logging.getLogger(__name__)

SLOW_QUERY_THRESHOLD_MS = 200

class QueryTimer:
    def __init__(self, operation_name: str, context: dict | None = None):
        self.operation_name = operation_name
        self.context = context or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        if duration_ms > SLOW_QUERY_THRESHOLD_MS:
            logger.warning(
                "Slow query detected",
                extra={
                    "operation": self.operation_name,
                    "duration_ms": round(duration_ms, 2),
                    **self.context,
                },
            )

# Usage:
# with QueryTimer("get_session_detail", {"session_id": session_id}):
#     result = await db.execute(query)
```

**Performance Tests:**

```python
# backend/tests/performance/test_api_performance.py
import pytest
import time
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_sessions_list_performance(client: AsyncClient, auth_headers: dict):
    start = time.perf_counter()
    response = await client.get("/api/v1/sessions", headers=auth_headers)
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    assert duration_ms < 300, f"Sessions list took {duration_ms:.2f}ms (expected <300ms)"

@pytest.mark.asyncio
async def test_session_creation_performance(client: AsyncClient, auth_headers: dict, job_posting_id: str, resume_id: str):
    start = time.perf_counter()
    response = await client.post(
        "/api/v1/sessions",
        json={"job_posting_id": job_posting_id, "resume_id": resume_id},
        headers=auth_headers,
    )
    duration_ms = (time.perf_counter() - start) * 1000

    assert response.status_code == 201
    assert duration_ms < 500, f"Session creation took {duration_ms:.2f}ms (expected <500ms)"
```

### Testing Requirements

**Test Coverage:**

- Critical GET endpoints <300ms
- Critical POST endpoints <500ms
- Database indexes exist
- No N+1 queries in session detail
- Slow query logging triggers correctly

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.9]
- [NFR1: Performance requirements]
- [NFR16: Database optimization]
- [Project Context: SQLAlchemy async patterns]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with performance standards and optimization checklist
- Includes index + eager loading patterns
- Adds slow query logging
- Adds performance tests
- Ready for dev implementation
