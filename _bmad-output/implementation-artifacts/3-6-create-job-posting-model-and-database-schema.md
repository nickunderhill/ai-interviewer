# Story 3.6: Create Job Posting Model and Database Schema

Status: done

## Story

As a developer, I want to create the JobPosting database model with user
association, so that users can store multiple job postings they want to practice
for.

## Acceptance Criteria

1. **Given** the User model exists **When** I create a JobPosting model in
   app/models/job_posting.py with fields (id, user_id, title, company,
   description, experience_level, tech_stack, created_at, updated_at) **Then**
   the JobPosting model uses SQLAlchemy 2.0+ declarative syntax **And** user_id
   is a foreign key to the users table **And** a one-to-many relationship is
   established (User has many JobPostings) **And** description field is Text
   type for job descriptions **And** tech_stack field stores comma-separated or
   JSON array of technologies **And** I generate and apply a migration to create
   the job_postings table

## Tasks / Subtasks

- [x] Task 1: Implement JobPosting ORM model (AC: #1)

  - [x] Create `backend/app/models/job_posting.py` with SQLAlchemy 2.0+
        declarative model
  - [x] Add fields: id (UUID PK), user_id (FK to users), title, company,
        description (Text), experience_level, tech_stack, created_at/updated_at
  - [x] Configure one-to-many relationship with User model
  - [x] Decide tech_stack storage format (JSONB or Text with comma-separated
        values)

- [x] Task 2: Create and apply Alembic migration (AC: #1)

  - [x] Import JobPosting model in alembic/env.py
  - [x] Generate migration:
        `alembic revision --autogenerate -m "create job_postings table"`
  - [x] Verify migration creates job_postings table with proper constraints
  - [x] Apply migration: `alembic upgrade head`
  - [x] Verify table naming follows plural_snake_case convention

- [x] Task 3: Add tests for JobPosting model (AC: #1)
  - [x] Test one-to-many relationship (user can have multiple job postings)
  - [x] Test required fields (title, description, user_id)
  - [x] Test optional fields (company, experience_level, tech_stack)
  - [x] Test description field accepts large text
  - [x] Test tech_stack storage and retrieval
  - [x] Test timestamps are UTC-aware

---

## Implementation Summary

**Status**: Completed on 2025-12-22

**Files Created**:

- `backend/app/models/job_posting.py` - JobPosting ORM model with JSONB
  tech_stack
- `backend/app/alembic/versions/20251222_1152_2d7b65cabd5b_create_job_postings_table.py` -
  Migration file
- `backend/tests/test_job_posting_model.py` - 9 comprehensive model tests

**Files Modified**:

- `backend/app/models/user.py` - Added job_postings relationship
- `backend/alembic/env.py` - Imported job_posting model
- `backend/tests/conftest.py` - Imported job_posting model

**Tests**: 9/9 passing

- test_create_job_posting_with_user
- test_one_to_many_relationship
- test_required_fields
- test_optional_fields_can_be_null
- test_description_field_accepts_large_text
- test_tech_stack_jsonb_storage
- test_timestamps_are_utc_aware
- test_cascading_delete
- test_user_job_postings_relationship

**Key Decisions**:

- Used JSONB for tech_stack column (native PostgreSQL array support)
- Indexed user_id foreign key for query performance
- Configured CASCADE delete (deleting user deletes job postings)
- All timestamps UTC-aware

## Dev Notes

### Critical Architecture Requirements

- Database naming: STRICT plural_snake_case for tables (job_postings),
  snake_case for columns
- SQLAlchemy 2.0+ async patterns required
- One-to-many relationship: User has many JobPostings, JobPosting belongs to one
  User
- Description field must support large text (job descriptions can be lengthy)
- Tech stack storage: Recommend JSONB for flexible array storage with PostgreSQL

### Technical Implementation Details

**Suggested files:**

- `backend/app/models/job_posting.py` - JobPosting ORM model
- `backend/alembic/versions/*_create_job_postings_table.py` - Migration file
- `backend/tests/test_job_posting_model.py` - Model tests

**JobPosting Model Structure:**

```python
from sqlalchemy.dialects.postgresql import JSONB

class JobPosting(Base):
    __tablename__ = "job_postings"

    id: UUID (primary key)
    user_id: UUID (foreign key to users, CASCADE on delete)
    title: String(255, nullable=False)
    company: String(255, nullable=True)
    description: Text (nullable=False)
    experience_level: String(50, nullable=True)  # e.g., "Junior", "Mid-level", "Senior"
    tech_stack: JSONB (nullable=True)  # Array of strings, e.g., ["Python", "React", "PostgreSQL"]
    created_at: DateTime(timezone=True)
    updated_at: DateTime(timezone=True)

    # Relationship
    user: Mapped[User] = relationship("User", back_populates="job_postings")
```

**User Model Update:**

- Add relationship:
  `job_postings: Mapped[List[JobPosting]] = relationship("JobPosting", back_populates="user", cascade="all, delete-orphan")`

**Foreign Key Configuration:**

- `user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)`
- Index on user_id for query performance (user will frequently query their own
  job postings)

**Tech Stack Storage Decision:**

- **Option A (Recommended):** JSONB column storing array of strings
  - Pros: Native PostgreSQL array support, queryable, flexible
  - Cons: PostgreSQL-specific (less portable)
- **Option B:** Text column with comma-separated values
  - Pros: Database-agnostic, simple
  - Cons: Not queryable, requires parsing in application layer
- **Recommendation:** Use JSONB for better data integrity and query capabilities

**Field Constraints:**

- title: NOT NULL, max 255 chars
- company: NULL allowed (user might not always specify)
- description: NOT NULL, Text type (no length limit)
- experience_level: NULL allowed, max 50 chars (e.g., "Junior", "Senior")
- tech_stack: NULL allowed, JSONB array

**Migration Considerations:**

- Verify foreign key constraint is created
- Verify index on user_id for query performance
- Verify cascading delete is configured
- Test migration rollback

**Testing Strategy:**

- Create user and multiple job postings, verify relationships
- Delete user, verify job postings are also deleted (cascade)
- Test optional fields can be null
- Test description field handles large text (e.g., 5KB+ job description)
- Test tech_stack JSONB storage and retrieval
- Verify timestamps are UTC-aware

### Dependencies

- Requires User model from Epic 2 (story 2.1)
- Requires Alembic configuration from Epic 1 (story 1.5)

### API Integration (Future Stories)

- This model will be consumed by Epic 3 job posting CRUD endpoints (stories
  3.7-3.11)
- Job posting data will be used as dual-context input for AI question generation
  in Epic 4
- Job posting will be referenced by InterviewSession model in Epic 4

### Security Considerations

- Job postings contain user's job search targets - ensure proper access control
- No sensitive data encryption needed (job descriptions are not confidential)
- Access control enforced via authentication middleware and user_id filtering

### Data Modeling Notes

- One-to-many relationship allows users to practice for multiple positions
- No unique constraints on title/company (user can save multiple postings for
  same company)
- Job postings are independent entities (no parent-child relationships between
  postings)
- Future consideration: If interview sessions reference job_postings, need to
  handle deletion (foreign key constraints)
