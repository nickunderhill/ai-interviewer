# Story 3.1: Create Resume Model and Database Schema

Status: done

## Story

As a developer, I want to create the Resume database model with user
association, so that users can store their résumé content in the system.

## Acceptance Criteria

1. **Given** the User model exists **When** I create a Resume model in
   app/models/resume.py with fields (id, user_id, content, created_at,
   updated_at) **Then** the Resume model uses SQLAlchemy 2.0+ declarative syntax
   **And** user_id is a foreign key to the users table **And** content field is
   Text type to store large résumé content **And** a one-to-one relationship is
   established between User and Resume **And** I generate and apply a migration
   to create the resumes table **And** cascading delete is configured (deleting
   user deletes résumé)

## Tasks / Subtasks

- [x] Task 1: Implement Resume ORM model (AC: #1)

  - [x] Create `backend/app/models/resume.py` with SQLAlchemy 2.0+ declarative
        model
  - [x] Add fields: id (UUID PK), user_id (FK to users with CASCADE), content
        (Text), created_at/updated_at (UTC timestamps)
  - [x] Configure one-to-one relationship with User model (backref or
        relationship on both sides)
  - [x] Ensure cascading delete (deleting user deletes résumé)

- [x] Task 2: Create and apply Alembic migration (AC: #1)

  - [x] Import Resume model in alembic/env.py
  - [x] Generate migration:
        `alembic revision --autogenerate -m "create resumes table"`
  - [x] Verify migration creates resumes table with proper constraints
  - [x] Apply migration: `alembic upgrade head`
  - [x] Verify table naming follows plural_snake_case convention

- [x] Task 3: Add tests for Resume model (AC: #1)
  - [x] Test one-to-one relationship (user can have one resume)
  - [x] Test cascading delete (deleting user deletes resume)
  - [x] Test content field accepts large text
  - [x] Test timestamps are UTC-aware

## Dev Notes

### Critical Architecture Requirements

- Database naming: STRICT plural_snake_case for tables (resumes), snake_case for
  columns
- SQLAlchemy 2.0+ async patterns required
- One-to-one relationship: User has one Resume, Resume belongs to one User
- Cascading delete essential for data integrity
- Never expose ORM models directly through API (use Pydantic schemas)

### Technical Implementation Details

**Suggested files:**

- `backend/app/models/resume.py` - Resume ORM model
- `backend/alembic/versions/*_create_resumes_table.py` - Migration file
- `backend/tests/test_resume_model.py` - Model tests

**Resume Model Structure:**

```python
class Resume(Base):
    __tablename__ = "resumes"

    id: UUID (primary key)
    user_id: UUID (foreign key to users, CASCADE on delete)
    content: Text (large text field for resume content)
    created_at: DateTime(timezone=True)
    updated_at: DateTime(timezone=True)

    # Relationship
    user: Mapped[User] = relationship("User", back_populates="resume")
```

**User Model Update:**

- Add relationship:
  `resume: Mapped[Optional[Resume]] = relationship("Resume", back_populates="user", uselist=False, cascade="all, delete-orphan")`

**Foreign Key Configuration:**

- `user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)`
- The `unique=True` constraint enforces one-to-one relationship at database
  level

**Migration Considerations:**

- Verify foreign key constraint is created
- Verify unique constraint on user_id
- Verify cascading delete is configured
- Test migration rollback

**Testing Strategy:**

- Create user and resume, verify relationship
- Delete user, verify resume is also deleted (cascade)
- Attempt to create two resumes for same user (should fail due to unique
  constraint)
- Verify content field handles large text (e.g., 10KB+ resume)
- Verify timestamps are UTC-aware with proper timezone info

### Dependencies

- Requires User model from Epic 2 (story 2.1)
- Requires Alembic configuration from Epic 1 (story 1.5)

### API Integration (Future Stories)

- This model will be consumed by Epic 3 resume CRUD endpoints (stories 3.2-3.5)
- Content field will be used as dual-context input for AI question generation in
  Epic 4

### Security Considerations

- Resume content may contain PII - ensure proper access control in API layer
- No sensitive data encryption required at model level (content is user's own
  data)
- Access control enforced via authentication middleware and user_id filtering

## Dev Agent Record

### Implementation Plan

- Story 3.1 creates the Resume model following the same patterns as the User
  model (SQLAlchemy 2.0+, UUID PK, timestamps)
- Implements one-to-one relationship with CASCADE delete
- Uses Text column type for large resume content storage
- Generates and applies Alembic migration

### Implementation Notes

- Created Resume ORM model in `backend/app/models/resume.py` with SQLAlchemy
  2.0+ declarative syntax
- Configured one-to-one relationship between User and Resume with `unique=True`
  on user_id FK
- Configured CASCADE delete on foreign key (deleting user deletes resume)
- Added `resume` relationship to User model with `cascade="all, delete-orphan"`
- Generated Alembic migration `130320381949_create_resumes_table.py`
- Applied migration to create resumes table with all constraints
- Created comprehensive model tests covering relationships, cascading, large
  text, and timestamps

### Tests Created

- test_create_resume_with_user: Verifies basic resume creation associated with
  user
- test_one_to_one_relationship: Confirms unique constraint prevents duplicate
  resumes per user
- test_cascading_delete: Validates cascade delete removes resume when user
  deleted
- test_content_field_accepts_large_text: Ensures Text field handles large
  content (> 10KB)
- test_timestamps_are_utc_aware: Verifies UTC timezone awareness on timestamps
- test_user_resume_relationship: Tests bidirectional relationship navigation

### Test Results

- All 6 resume model tests pass
- No regressions in existing user model tests
- Async API tests continue to pass

### Completion Notes

✅ All tasks completed successfully:

- Task 1: Resume ORM model implemented with all required fields and
  relationships
- Task 2: Alembic migration generated and applied (revision 130320381949)
- Task 3: Comprehensive tests added and passing

### Code Review Fixes (2025-12-22)

✅ **Issue #1 (HIGH):** Added database index on resumes.user_id foreign key

- Created migration `ca77a739011c_add_index_resumes_user_id.py`
- Applied migration to add `ix_resumes_user_id` index
- Addresses Epic 8.9/8.13 performance requirements

✅ **Issue #2 (MEDIUM):** Removed unused String import from resume.py

✅ **Issue #3 (MEDIUM):** Added TYPE_CHECKING guard for User import

- Matches pattern established in user.py
- Fixes type checker errors

✅ **Issue #4 (MEDIUM):** Added onupdate=utcnow to updated_at field

- Ensures timestamp auto-updates on modifications
- Matches User model pattern

✅ **Issue #5 (LOW-MEDIUM):** Enhanced bidirectional relationship test

- Added explicit assertions for resume.user navigation
- Verifies back_populates correctness in both directions

All 6 tests passing. Ready for merge.

## File List

Files created:

- `backend/app/models/resume.py` - Resume ORM model
- `backend/alembic/versions/20251222_0655_130320381949_create_resumes_table.py` -
  Migration for resumes table
- `backend/alembic/versions/20251222_0756_ca77a739011c_add_index_resumes_user_id.py` -
  Migration for user_id index (code review fix)
- `backend/tests/test_resume_model.py` - Resume model tests

Files modified:

- `backend/app/models/user.py` - Added resume relationship
- `backend/alembic/env.py` - Imported resume model for migration discovery
- `backend/tests/conftest.py` - Imported resume model for test schema creation

## Change Lo 07:56: Code review fixes - added user_id index migration, removed unused import, added TYPE_CHECKING guard, fixed onupdate, enhanced tests

- 2025-12-22 06:55g

- 2025-12-22: Created Resume model with one-to-one relationship to User,
  generated and applied migration, added comprehensive tests
