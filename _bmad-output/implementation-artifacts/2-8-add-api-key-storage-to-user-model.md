# Story 2.8: Add API Key Storage to User Model

Status: ready-for-dev

## Story

As a developer, I want to add encrypted API key storage to the User model, so
that users can securely store their OpenAI API keys.

## Acceptance Criteria

1. **Given** the User model exists **When** I add an `encrypted_api_key` field
   to the User model **Then** the field is a String type that can store
   encrypted data **And** the field is nullable (users may not have configured
   their API key yet) **And** I generate a migration with
   `alembic revision --autogenerate -m "add encrypted_api_key to users"` **And**
   running `alembic upgrade head` adds the column to the users table

## Tasks / Subtasks

- [ ] Task 1: Update `User` model (AC: #1)

  - [ ] Add `encrypted_api_key` nullable string column

- [ ] Task 2: Create and apply Alembic migration (AC: #1)

  - [ ] Autogenerate migration
  - [ ] Apply migration to DB

- [ ] Task 3: Add basic tests (AC: #1)
  - [ ] Verify column exists and is nullable

## Dev Notes

### Critical Architecture Requirements

- API keys must be encrypted at rest; this story only adds storage column.
- API keys must never be exposed to the frontend.

### Technical Implementation Details

- Suggested files:
  - `backend/app/models/user.py`
  - `backend/alembic/versions/*_add_encrypted_api_key_to_users.py`
