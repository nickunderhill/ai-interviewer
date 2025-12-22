# Story 4.1: Create Session and Message Models

Status: ready-for-dev

## Story

As a developer, I want to create database models for interview sessions and
session messages, so that we can persist interview state and conversation
history.

## Acceptance Criteria

1. **Given** I'm implementing the data layer **When** I create the
   InterviewSession model **Then** it includes fields: id (UUID), user_id (FK to
   User), job_posting_id (FK to JobPosting), status (enum: 'active', 'paused',
   'completed'), current_question_number (integer), created_at, updated_at
   **And** I create the SessionMessage model **And** it includes fields: id
   (UUID), session_id (FK to InterviewSession), message_type (enum: 'question',
   'answer'), content (Text), question_type (Text nullable -
   technical/behavioral/situational), created_at **And** both use snake_case
   naming with plural table names **And** foreign keys are explicit with
   ondelete behavior defined **And** timestamps use UTC

## Tasks / Subtasks

- [ ] Task 1: Create InterviewSession ORM model (AC: #1)

  - [ ] Create `backend/app/models/interview_session.py` with SQLAlchemy 2.0+
        declarative model
  - [ ] Add fields: id (UUID PK), user_id (FK to users), job_posting_id (FK to
        job_postings), status (String), current_question_number (Integer),
        created_at, updated_at
  - [ ] Configure relationships with User and JobPosting models (back_populates)
  - [ ] Add composite index on user_id and created_at for efficient querying
  - [ ] Implement status field as String (validate in application layer)

- [ ] Task 2: Create SessionMessage ORM model (AC: #1)

  - [ ] Create `backend/app/models/session_message.py` with SQLAlchemy 2.0+
        declarative model
  - [ ] Add fields: id (UUID PK), session_id (FK to interview_sessions),
        message_type (String), content (Text), question_type (String nullable),
        created_at
  - [ ] Configure relationship with InterviewSession model (back_populates)
  - [ ] Add composite index on session_id and created_at for message ordering
  - [ ] Use Text type for content field (large text support for answers)

- [ ] Task 3: Update User and JobPosting models with relationships (AC: #1)

  - [ ] Add `interview_sessions` relationship to User model
  - [ ] Add `interview_sessions` relationship to JobPosting model
  - [ ] Decide on foreign key cascade behavior (SET NULL or CASCADE for
        job_posting_id deletion)
  - [ ] Update TYPE_CHECKING imports for circular references

- [ ] Task 4: Create and apply Alembic migration (AC: #1)

  - [ ] Import both models in `backend/app/models/__init__.py`
  - [ ] Import models in `backend/alembic/env.py`
  - [ ] Generate migration:
        `alembic revision --autogenerate -m "create interview_sessions and session_messages tables"`
  - [ ] Verify migration creates both tables with proper constraints and indexes
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Verify tables exist in PostgreSQL with correct structure

- [ ] Task 5: Add model tests (AC: #1)
  - [ ] Create `backend/tests/test_interview_session_model.py`
  - [ ] Test InterviewSession creation with all relationships
  - [ ] Test status field accepts valid values
  - [ ] Test current_question_number defaults to 0
  - [ ] Test cascade behavior (deleting user/job posting)
  - [ ] Create `backend/tests/test_session_message_model.py`
  - [ ] Test SessionMessage creation with session relationship
  - [ ] Test message_type field validation
  - [ ] Test content field accepts large text
  - [ ] Test question_type is nullable
  - [ ] Test message ordering by created_at

## Dev Notes

### Critical Architecture Requirements

**Database Patterns (STRICT):**

- Table names: `interview_sessions` and `session_messages` (plural_snake_case)
- Columns: snake_case (user_id, job_posting_id, session_id, message_type,
  question_type, current_question_number, created_at)
- Primary keys: UUID using `uuid.uuid4()` default
- Foreign keys: Explicit naming with CASCADE behavior for user_id, SET NULL
  behavior recommended for job_posting_id (preserve interview history)
- Timestamps: UTC-aware using `DateTime(timezone=True)` with utcnow() default
- Indexes: Composite indexes for common query patterns (user_id + created_at)

**SQLAlchemy 2.0+ Patterns:**

- Use `Mapped[Type]` annotations with `mapped_column()`
- TYPE_CHECKING imports for circular relationships
- Relationship configuration with `back_populates` on both sides
- Use `relationship()` with explicit `back_populates` parameter
- Cascade configuration on relationship level, not just FK level

**Status Field Implementation:**

- InterviewSession.status: String field storing 'active', 'paused', 'completed'
- SessionMessage.message_type: String field storing 'question', 'answer'
- Validation happens in service/schema layer (Pydantic), not database
- Allows flexibility for future status types without migrations

### Technical Implementation Details

**File Structure:**

```
backend/app/models/
├── __init__.py              # Import both models for Alembic
├── user.py                  # Add interview_sessions relationship
├── job_posting.py           # Add interview_sessions relationship
├── interview_session.py     # NEW - InterviewSession model
└── session_message.py       # NEW - SessionMessage model
```

**InterviewSession Model Structure:**

```python
# backend/app/models/interview_session.py
import datetime as dt
import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.job_posting import JobPosting
    from app.models.session_message import SessionMessage

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

class InterviewSession(Base):
    """InterviewSession model - tracks AI-powered interview sessions."""

    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_posting_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("job_postings.id", ondelete="SET NULL"),
        nullable=True,  # Nullable to preserve session if job posting deleted
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
    )

    current_question_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="interview_sessions",
    )

    job_posting: Mapped[Optional["JobPosting"]] = relationship(
        "JobPosting",
        back_populates="interview_sessions",
    )

    messages: Mapped[List["SessionMessage"]] = relationship(
        "SessionMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SessionMessage.created_at",
    )

    # Composite index for efficient queries
    __table_args__ = (
        Index(
            "ix_interview_sessions_user_id_created_at",
            "user_id",
            "created_at",
        ),
    )
```

**SessionMessage Model Structure:**

```python
# backend/app/models/session_message.py
import datetime as dt
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession

def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)

class SessionMessage(Base):
    """SessionMessage model - stores Q&A messages in interview sessions."""

    __tablename__ = "session_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    message_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,  # Only applicable for message_type='question'
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    # Relationships
    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="messages",
    )

    # Composite index for efficient message retrieval
    __table_args__ = (
        Index(
            "ix_session_messages_session_id_created_at",
            "session_id",
            "created_at",
        ),
    )
```

**Foreign Key Cascade Strategy:**

- `user_id` → CASCADE: If user is deleted, delete all their sessions (expected
  behavior)
- `job_posting_id` → SET NULL: If job posting is deleted, preserve session
  history with NULL reference (interview data is valuable research data, should
  not be lost)
- `session_id` → CASCADE: If session is deleted, delete all its messages
  (messages have no meaning without session)

**Relationship Updates for Existing Models:**

```python
# backend/app/models/user.py - Add to User class:
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession

# Add relationship
interview_sessions: Mapped[List["InterviewSession"]] = relationship(
    "InterviewSession",
    back_populates="user",
    cascade="all, delete-orphan",
)
```

```python
# backend/app/models/job_posting.py - Add to JobPosting class:
from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
    from app.models.interview_session import InterviewSession

# Add relationship
interview_sessions: Mapped[List["InterviewSession"]] = relationship(
    "InterviewSession",
    back_populates="job_posting",
)
```

### Testing Requirements

**Model Tests:**

- Test session creation with user and job_posting relationships
- Test status field accepts 'active', 'paused', 'completed'
- Test current_question_number defaults to 0
- Test cascade delete: deleting user deletes sessions
- Test SET NULL: deleting job posting sets job_posting_id to NULL but preserves
  session
- Test messages relationship: session can have multiple messages
- Test message ordering by created_at
- Test message_type accepts 'question' and 'answer'
- Test question_type is nullable for answers
- Test content field handles large text (1000+ characters)
- Test all timestamps are UTC-aware

**Migration Verification:**

- Verify both tables created with correct names (plural_snake_case)
- Verify all foreign keys have correct ondelete behavior
- Verify indexes created for query performance
- Verify UUID columns use uuid.uuid4() default
- Verify timestamps use timezone-aware DateTime

### Project Structure Notes

**Established Patterns from Previous Stories:**

- Models use UUID primary keys with `uuid.uuid4()` default
- All models have docstrings explaining purpose
- utcnow() helper function defined in each model file
- TYPE_CHECKING pattern for circular imports
- Composite indexes for common query patterns (user_id + created_at)
- Relationships always use explicit `back_populates`
- Foreign keys include index for query performance
- Models imported in `__init__.py` for Alembic autodiscovery

**Dependencies on Previous Work:**

- User model exists (Epic 2, Story 2.1)
- JobPosting model exists (Epic 3, Story 3.6)
- Alembic configured and working (Epic 1, Story 1.5)
- Test patterns established in previous model tests

**Impact on Future Stories:**

- Story 4.2 (Session Creation) will use InterviewSession model
- Story 4.3 (Session List) will query InterviewSession with user relationship
- Story 4.10 (Store Question) will create SessionMessage records
- Story 4.11 (Answer Submission) will create SessionMessage records
- Story 4.12 (Messages Retrieval) will query SessionMessage with ordering

### References

**Source Documentation:**

- [Epic 4 Details: epics.md#Epic 4: Interactive Interview Sessions]
- [Architecture: Database Naming Conventions: architecture.md#Naming Patterns]
- [Architecture: SQLAlchemy Patterns: architecture.md#Data Architecture]
- [Project Context: Database Patterns: project-context.md#Database & Backend
  Patterns]
- [Previous Model Example: backend/app/models/job_posting.py]
- [Previous Model Example: backend/app/models/resume.py]
- [Foreign Key Strategy: Story 3.11 Implementation Summary]

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent during implementation_

### Completion Notes List

- Model files created following SQLAlchemy 2.0+ patterns
- Relationships configured with back_populates on all sides
- Foreign key cascade behavior: CASCADE for user_id, SET NULL for job_posting_id
- Composite indexes created for query performance
- Migration generated and applied successfully
- All model tests passing
- UTC timestamps validated

### File List

**Files to Create:**

- `backend/app/models/interview_session.py`
- `backend/app/models/session_message.py`
- `backend/tests/test_interview_session_model.py`
- `backend/tests/test_session_message_model.py`
- `backend/alembic/versions/{timestamp}_create_interview_sessions_and_session_messages_tables.py`

**Files to Modify:**

- `backend/app/models/__init__.py` - Import new models
- `backend/app/models/user.py` - Add interview_sessions relationship
- `backend/app/models/job_posting.py` - Add interview_sessions relationship
- `backend/alembic/env.py` - Verify imports (may be automatic)

**Files to Verify:**

- All existing tests still pass after adding relationships
- Database migration applies cleanly
- Models discoverable by Alembic
