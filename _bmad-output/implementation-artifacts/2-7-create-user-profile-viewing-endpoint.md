# Story 2.7: Create User Profile Viewing Endpoint

Status: ready-for-dev

## Story

As a user, I want to view my profile information, so that I can see my account
details.

## Acceptance Criteria

1. **Given** I am authenticated with a valid JWT token **When** I GET
   `/api/v1/users/me` with my JWT token in the Authorization header **Then** the
   system returns my user profile (id, email, created_at) **And** the password
   hash is never included in the response **And** requests without a token
   return 401 Unauthorized **And** the endpoint uses the `get_current_user`
   dependency for authentication

## Tasks / Subtasks

- [ ] Task 1: Add profile response schema (AC: #1)

  - [ ] Create Pydantic schema for user profile view

- [ ] Task 2: Implement `GET /api/v1/users/me` endpoint (AC: #1)

  - [ ] Use `get_current_user` dependency
  - [ ] Return profile fields only (no hashed password)

- [ ] Task 3: Add endpoint tests (AC: #1)
  - [ ] No token returns 401
  - [ ] Valid token returns expected user fields

## Dev Notes

### Critical Architecture Requirements

- Data isolation: endpoint must always return the authenticated user only.
- Never include `hashed_password` in any response.

### Technical Implementation Details

- Suggested files:
  - `backend/app/api/v1/endpoints/users.py`
  - `backend/app/schemas/users.py`
  - `backend/tests/api/v1/test_users_me.py`
