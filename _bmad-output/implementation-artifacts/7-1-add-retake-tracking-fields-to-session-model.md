# Story 7.1: Add Retake Tracking Fields to Session Model

Status: ready-for-dev

## Story

As a developer, I want to extend the InterviewSession model for retake tracking,
so that we can link retakes and track attempt numbers.

## Acceptance Criteria

1. **Given** I'm enhancing the session model **When** I add retake tracking
   fields **Then** the InterviewSession model includes: `retake_number`
   (Integer, default 1), `original_session_id` (UUID nullable, FK to
   InterviewSession self-reference) **And** retake_number indicates which
   attempt this is (1 = first attempt, 2 = first retake, etc.) **And**
   original_session_id points to the very first session for this job posting
   (null for original attempts) **And** the database migration adds these fields
   with default values for existing sessions **And** uses snake_case naming
   conventions ✅

## Tasks / Subtasks

- [ ] Task 1: Update InterviewSession model with retake tracking fields (AC: #1)

  - [ ] Add `retake_number` field: `Mapped[int]` with default=1
  - [ ] Add `original_session_id` field: `Mapped[Optional[uuid.UUID]]` nullable,
        FK to interview_sessions.id
  - [ ] Add self-referential relationship for tracking retakes
  - [ ] Ensure snake_case naming conventions
  - [ ] Follow SQLAlchemy 2.0+ async patterns

- [ ] Task 2: Create Alembic migration for new fields (AC: #1)

  - [ ] Generate migration:
        `alembic revision --autogenerate -m "Add retake tracking to interview_sessions"`
  - [ ] Add `retake_number` column: Integer, default=1, not null
  - [ ] Add `original_session_id` column: UUID, nullable, FK to
        interview_sessions(id)
  - [ ] Set default values for existing sessions (retake_number=1,
        original_session_id=NULL)
  - [ ] Add index on original_session_id for query performance
  - [ ] Test migration: up and down operations

- [ ] Task 3: Update InterviewSession Pydantic schemas (AC: #1)

  - [ ] Update SessionResponse schema: include retake_number and
        original_session_id
  - [ ] Update SessionCreate/SessionUpdate if needed
  - [ ] Ensure proper typing: retake_number (int), original_session_id
        (Optional[UUID])
  - [ ] Add field descriptions for documentation

- [ ] Task 4: Test retake fields in session creation (AC: #1)
  - [ ] Test creating new session: retake_number=1, original_session_id=None by
        default
  - [ ] Verify schema validation for retake fields
  - [ ] Test querying sessions with retake relationships
  - [ ] Test backward compatibility with existing sessions

## Dev Notes

### Critical Architecture Requirements

**Database & Backend:**

- **Python:** 3.11+
- **Framework:** FastAPI with SQLAlchemy 2.0+ async
- **Database:** PostgreSQL with snake_case naming
- **Migrations:** Alembic for schema changes
- **Model Location:** `backend/app/models/interview_session.py`
- **Schema Location:** `backend/app/schemas/session.py`

**Key Technical Patterns:**

- Use `Mapped[T]` type hints (SQLAlchemy 2.0 style)
- Use `mapped_column()` for column definitions
- Self-referential FK:
  `ForeignKey("interview_sessions.id", ondelete="SET NULL")`
- Default values must be set in both model and migration
- All timestamps: UTC with `DateTime(timezone=True)`

### Existing Model Context

**Current InterviewSession Model Fields:**

```python
# From: backend/app/models/interview_session.py
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID]  # Primary key
    user_id: Mapped[uuid.UUID]  # FK to users.id
    job_posting_id: Mapped[Optional[uuid.UUID]]  # FK to job_postings.id, nullable
    status: Mapped[str]  # default="active"
    current_question_number: Mapped[int]  # default=0
    created_at: Mapped[dt.datetime]  # UTC timestamp
    updated_at: Mapped[dt.datetime]  # UTC timestamp with onupdate

    # Relationships: user, job_posting, messages, feedback
```

**New Fields to Add:**

```python
retake_number: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    default=1,
)

original_session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID(as_uuid=True),
    ForeignKey("interview_sessions.id", ondelete="SET NULL"),
    nullable=True,
    index=True,
)

# Add relationship for querying retakes
original_session: Mapped[Optional["InterviewSession"]] = relationship(
    "InterviewSession",
    remote_side=[id],
    back_populates="retakes",
)

retakes: Mapped[List["InterviewSession"]] = relationship(
    "InterviewSession",
    back_populates="original_session",
)
```

### Migration Example Pattern

```python
# Migration upgrade() example
def upgrade() -> None:
    # Add retake_number column with default
    op.add_column('interview_sessions',
        sa.Column('retake_number', sa.Integer(), nullable=False, server_default='1'))

    # Add original_session_id column (nullable)
    op.add_column('interview_sessions',
        sa.Column('original_session_id',
                  sa.dialects.postgresql.UUID(as_uuid=True),
                  nullable=True))

    # Add FK constraint
    op.create_foreign_key('fk_interview_sessions_original_session_id',
                         'interview_sessions', 'interview_sessions',
                         ['original_session_id'], ['id'],
                         ondelete='SET NULL')

    # Add index for query performance
    op.create_index('ix_interview_sessions_original_session_id',
                   'interview_sessions', ['original_session_id'])

def downgrade() -> None:
    op.drop_index('ix_interview_sessions_original_session_id')
    op.drop_constraint('fk_interview_sessions_original_session_id', 'interview_sessions')
    op.drop_column('interview_sessions', 'original_session_id')
    op.drop_column('interview_sessions', 'retake_number')
```

### Schema Update Pattern

```python
# In backend/app/schemas/session.py
class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_posting_id: Optional[UUID]
    status: str
    current_question_number: int
    retake_number: int  # ADD THIS
    original_session_id: Optional[UUID]  # ADD THIS
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### Testing Checklist

- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] Migration rollback works: `alembic downgrade -1`
- [ ] Existing sessions have retake_number=1 after migration
- [ ] New sessions created with correct defaults
- [ ] Self-referential relationship queries work
- [ ] Schema serialization includes new fields
- [ ] API responses include retake fields

### Project Structure References

**Files to Modify:**

- `backend/app/models/interview_session.py` - Add fields and relationships
- `backend/app/schemas/session.py` - Update Pydantic schemas
- `backend/alembic/versions/` - Create new migration file

**Testing:**

- Run migration in test database
- Test CRUD operations on sessions
- Verify backward compatibility

### Related Context

**From Project Context
([project-context.md](../_bmad-output/project-context.md)):**

- Database naming: `plural_snake_case` tables, `snake_case` columns
- Foreign keys: explicit naming (e.g., `original_session_id`)
- SQLAlchemy: Use async patterns with `Mapped[T]` and `mapped_column()`
- All timestamps: `DateTime(timezone=True)` with UTC

**From Architecture ([architecture.md](../_bmad-output/architecture.md)):**

- InterviewSession tracks interview state and progress
- Self-referential FK pattern for parent-child relationships
- Retake functionality enables improvement tracking (FR52-56)

**From Epic 7 ([epics.md](../_bmad-output/epics.md)):**

- Epic 7 Goal: Enable retake tracking and score comparison
- Story 7.1 is foundation for all retake features
- Subsequent stories (7.2-7.5) depend on these fields

### Anti-Patterns to Avoid

❌ Don't use camelCase: `retakeNumber`, `originalSessionId`  
❌ Don't forget index on FK for query performance  
❌ Don't forget server_default='1' in migration for existing rows  
❌ Don't expose SQLAlchemy models directly - use Pydantic schemas  
❌ Don't forget both upgrade() and downgrade() in migration

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent_
