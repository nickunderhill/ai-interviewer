# Story 2.5: Create User Login Endpoint

Status: ready-for-dev

## Story

As a user, I want to log in with my email and password, so that I can access my
account and interview sessions.

## Acceptance Criteria

1. **Given** a user has registered an account **When** I POST to
   `/api/v1/auth/login` with correct email and password **Then** the system
   verifies the password against the hashed password in the database **And** a
   JWT access token is generated and returned **And** the response includes
   `{"access_token": "...", "token_type": "bearer"}` **And** incorrect password
   returns 401 Unauthorized **And** non-existent email returns 401 Unauthorized
   **And** the token can be used to authenticate subsequent API requests

## Tasks / Subtasks

- [ ] Task 1: Add login schemas (AC: #1)

  - [ ] Request schema (email, password)
  - [ ] Response schema (`access_token`, `token_type`)

- [ ] Task 2: Implement login endpoint (AC: #1)

  - [ ] Verify email exists
  - [ ] Verify password using bcrypt helper
  - [ ] Create JWT access token with user_id
  - [ ] Return 401 for invalid credentials without leaking which part failed

- [ ] Task 3: Add endpoint tests (AC: #1)
  - [ ] Successful login returns bearer token
  - [ ] Wrong password returns 401
  - [ ] Unknown email returns 401

## Dev Notes

### Critical Architecture Requirements

- JWT format: `Authorization: Bearer {token}` for subsequent calls.
- Tokens are stateless (no server-side session storage).

### Technical Implementation Details

- Suggested files:
  - `backend/app/api/v1/endpoints/auth.py`
  - `backend/app/schemas/auth.py`
  - `backend/app/services/auth_service.py`
  - `backend/tests/api/v1/test_auth_login.py`
