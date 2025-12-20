# Story 2.1: Create User Model and Database Schema

Status: ready-for-dev

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

- [ ] Task 1: Implement `User` ORM model (AC: #1)

  - [ ] Create `backend/app/models/user.py` with SQLAlchemy declarative model
  - [ ] Add `email` unique constraint and non-null constraints
  - [ ] Add `created_at` / `updated_at` timezone-aware UTC timestamps

- [ ] Task 2: Create and apply Alembic migration (AC: #1)

  - [ ] Autogenerate migration for `users` table
  - [ ] Verify table/column naming follows snake_case conventions
  - [ ] Apply migration to development DB

- [ ] Task 3: Add minimal tests around schema expectations (AC: #1)
  - [ ] Verify unique email constraint enforced
  - [ ] Verify timestamps are populated and timezone-aware

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
