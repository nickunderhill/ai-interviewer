# Story 5.1: Create Feedback Model

Status: review

## Story

As a developer, I want to create a database model for interview feedback, so
that we can persist AI-generated analysis results.

## Acceptance Criteria

1. **Given** I'm implementing the feedback data layer **When** I create the
   InterviewFeedback model **Then** it includes fields: id (UUID), session_id
   (FK to InterviewSession, unique one-to-one), technical_accuracy_score
   (Integer 0-100), communication_clarity_score (Integer 0-100),
   problem_solving_score (Integer 0-100), relevance_score (Integer 0-100),
   overall_score (Integer 0-100), technical_feedback (Text),
   communication_feedback (Text), problem_solving_feedback (Text),
   relevance_feedback (Text), overall_comments (Text), knowledge_gaps (JSON
   array), learning_recommendations (JSON array), created_at, updated_at **And**
   uses snake_case naming with plural table name **And** timestamps use UTC
   **And** the one-to-one relationship ensures each session has at most one
   feedback record

## Tasks / Subtasks

- [x] Task 1: Create InterviewFeedback ORM model (AC: #1)

  - [x] Create `backend/app/models/interview_feedback.py`
  - [x] Use plural_snake_case table naming (`interview_feedbacks`)
  - [x] Add `id` UUID PK (uuid4 default)
  - [x] Add `session_id` UUID FK → `interview_sessions.id` with **unique
        constraint** (enforces one-to-one)
  - [x] Add 5 score columns as Integer with app-level validation (0..100)
  - [x] Add 5 feedback text columns as `Text`
  - [x] Add `knowledge_gaps` and `learning_recommendations` as JSONB storing
        arrays
  - [x] Add `created_at`/`updated_at` timezone-aware UTC
  - [x] Add relationship:
        `session: Mapped[InterviewSession] = relationship(..., back_populates="feedback")`

- [x] Task 2: Wire relationships on InterviewSession (AC: #1)

  - [x] Update `backend/app/models/interview_session.py` to add `feedback`
        relationship (one-to-one)
  - [x] Use `uselist=False` on relationship

- [x] Task 3: Add Alembic migration (AC: #1)

  - [x] Import model in `backend/app/models/__init__.py`
  - [x] Generate migration:
        `alembic revision --autogenerate -m "create interview feedback table"`
  - [x] Ensure migration creates:
    - [x] table with correct name and columns
    - [x] FK constraint on `session_id`
    - [x] unique constraint or unique index on `session_id`
    - [x] JSONB column types in PostgreSQL
  - [x] Apply migration: `alembic upgrade head`

- [x] Task 4: Create Pydantic schemas (AC: #1)

  - [x] Create `backend/app/schemas/feedback.py`
  - [x] `InterviewFeedbackResponse` includes all fields returned by API (no
        internal-only fields)
  - [x] Use Pydantic v2 `ConfigDict(from_attributes=True)`

- [x] Task 5: Add model-level tests (AC: #1)

  - [x] Create `backend/tests/test_interview_feedback_model.py`
  - [x] Test one-to-one constraint: cannot create two feedback records for same
        session
  - [x] Test JSON array fields round-trip lists
  - [x] Test timestamps are UTC-aware

## Dev Notes

### Critical Architecture Requirements

- **SQLAlchemy 2.0 async patterns** only.
- **Naming (STRICT):** plural_snake_case for tables, snake_case for columns.
- **One-to-one enforcement:** must be guaranteed at DB level via unique
  constraint on `session_id`.
- **UTC timestamps:** `DateTime(timezone=True)` with `dt.timezone.utc`.
- **JSON arrays:** store `knowledge_gaps` and `learning_recommendations` as
  PostgreSQL JSONB.

### Technical Implementation Details

**Suggested file structure:**

```
backend/app/
├── models/
│   ├── interview_feedback.py     # NEW
│   ├── interview_session.py      # UPDATE (feedback relationship)
│   └── __init__.py               # UPDATE (import InterviewFeedback)
├── schemas/
│   └── feedback.py               # NEW
└── alembic/versions/
    └── *_create_interview_feedback_table.py  # NEW

backend/tests/
└── test_interview_feedback_model.py          # NEW
```

**Model sketch (align with existing patterns in
`backend/app/models/operation.py`):**

```python
import datetime as dt
import uuid
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

class InterviewFeedback(Base):
    __tablename__ = "interview_feedbacks"  # confirm naming

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    technical_accuracy_score: Mapped[int] = mapped_column(Integer, nullable=False)
    communication_clarity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    problem_solving_score: Mapped[int] = mapped_column(Integer, nullable=False)
    relevance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)

    technical_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    communication_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    problem_solving_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_feedback: Mapped[str] = mapped_column(Text, nullable=False)
    overall_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    knowledge_gaps: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    learning_recommendations: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    session = relationship("InterviewSession", back_populates="feedback")
```

### Dependencies / Cross-Story Context

- Depends on models from Epic 4: `InterviewSession` and `SessionMessage`.
- Feeds Epic 5 story 5.5 (feedback retrieval endpoint) and story 6.\* (history
  views).

### References

- [Epic 5 Details: _bmad-output/epics.md#Epic 5: AI-Powered Feedback & Analysis]
- [Project Context: _bmad-output/project-context.md#Database & Backend Patterns]
- Prior model patterns: `backend/app/models/operation.py`,
  `backend/app/models/interview_session.py`

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Debug Log References

N/A - no blockers encountered.

### Completion Notes List

- ✅ InterviewFeedback model created with plural table name
  (interview_feedbacks)
- ✅ One-to-one session→feedback enforced with unique constraint on session_id
- ✅ JSONB arrays store knowledge_gaps and learning_recommendations as
  PostgreSQL JSONB
- ✅ UTC timestamps verified (DateTime(timezone=True) with utcnow() default)
- ✅ Alembic migration generated and applied successfully
  (20251225_0154_127d39341e56)
- ✅ InterviewSession.feedback relationship added with uselist=False for
  one-to-one access
- ✅ Pydantic InterviewFeedbackResponse schema created with
  ConfigDict(from_attributes=True)
- ✅ 8 comprehensive model tests added covering one-to-one constraint, JSON
  round-trip, UTC timestamps, cascade deletes, relationship access
- ✅ All 363 backend tests passing (100% pass rate)

### File List

backend/app/models/interview_feedback.py backend/app/models/interview_session.py
backend/app/models/**init**.py backend/app/schemas/feedback.py
backend/alembic/env.py
backend/alembic/versions/20251225_0154_127d39341e56_create_interview_feedback_table.py
backend/tests/conftest.py backend/tests/test_interview_feedback_model.py
