# Story 2.1: Create User Model and Database Schema

Status: done

## Story

As a developer, I want to create the User database model with fields for
authentication and profile, so that user data can be securely stored in
PostgreSQL.

## Acceptance Criteria

1. **Given** Alembic is configured for migrations **When** I create a User model
   in app/models/user.py with fields (id, email, hashed_password, created_at,
   updated_at) **Then** the User model uses SQLAlchemy 2.0+ declarative syntax
   **And** email field has a unique constraint **And** timestamps use
   DateTime(timezone=True) with UTC **And** I generate a migration with
   `alembic revision --autogenerate -m "create users table"` **And** running
   `alembic upgrade head` creates the users table in PostgreSQL **And** the
   table follows snake_case naming convention

## Tasks / Subtasks

- [x] Task 1: Implement `User` ORM model (AC: #1)

  - [x] Create `backend/app/models/user.py` with SQLAlchemy declarative model
  - [x] Add `email` unique constraint and non-null constraints
  - [x] Add `created_at` / `updated_at` timezone-aware UTC timestamps

- [x] Task 2: Create and apply Alembic migration (AC: #1)

  - [x] Autogenerate migration for `users` table
  - [x] Verify table/column naming follows snake_case conventions
  - [x] Apply migration to development DB

- [x] Task 3: Add minimal tests around schema expectations (AC: #1)
  - [x] Verify unique email constraint enforced
  - [x] Verify timestamps are populated and timezone-aware

## Dev Notes

### Critical Architecture Requirements

- Backend uses SQLAlchemy 2.0+ async patterns and Alembic migrations.
- Database naming is STRICT: plural_snake_case for tables, snake_case for
  columns.
- Never expose ORM models directly through API responses (use Pydantic schemas).

### Technical Implementation Details

- Suggested files:
  - `backend/app/models/user.py`
  - `backend/alembic/versions/*_create_users_table.py`
- Recommended fields:
  - `id`: UUID primary key
  - `email`: unique indexed string
  - `hashed_password`: string
  - `created_at`, `updated_at`: timezone-aware timestamps (UTC)

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Implementation Notes

- Implemented SQLAlchemy 2.0 declarative `User` model with UUID PK, unique
  email, and timezone-aware timestamps.
- Registered model import in Alembic env so `--autogenerate` discovers metadata.
- Generated and applied Alembic migration `75cc412b7425`.

### Test Results

- `DB_HOST=localhost pytest -q` (71 passed)

## File List

Files created:

- `backend/app/models/user.py`
- `backend/alembic/versions/20251220_0522_75cc412b7425_create_users_table.py`
- `backend/tests/test_user_model.py`

Files modified:

- `backend/alembic/env.py`
- `backend/tests/conftest.py`

## Change Log

- 2025-12-20: Added `users` table model + migration + schema tests.
- 2025-12-20: Senior review fixes: isolated test DB schema + assert UTC
  timestamps.

## Senior Developer Review (AI)

**Date:** 2025-12-20

**Outcome:** Approved (changes applied)

**Findings addressed:**

- HIGH: Prevented destructive test DB behavior by running schema creation in an
  isolated, per-test Postgres schema.
- MEDIUM: Strengthened timestamp test to assert UTC (offset 0), not just
  tz-aware.
