# Story 2.5: Create User Login Endpoint

Status: done

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

- [x] Task 1: Add login schemas (AC: #1)

  - [x] Request schema (email, password)
  - [x] Response schema (`access_token`, `token_type`)

- [x] Task 2: Implement login endpoint (AC: #1)

  - [x] Verify email exists
  - [x] Verify password using bcrypt helper
  - [x] Create JWT access token with user_id
  - [x] Return 401 for invalid credentials without leaking which part failed

- [x] Task 3: Add endpoint tests (AC: #1)
  - [x] Successful login returns bearer token
  - [x] Wrong password returns 401
  - [x] Unknown email returns 401

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

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Implementation Notes

- Added `/api/v1/auth/login` that authenticates via bcrypt hash verification and
  returns a JWT access token.
- Returns 401 for invalid credentials using a single error shape to avoid
  leaking whether email or password was wrong.

### Test Results

- `pytest -q` (94 passed)

## File List

Files created:

- `backend/app/api/deps.py`
- `backend/app/services/auth_service.py`
- `backend/tests/api/v1/test_auth_login.py`
- `backend/tests/services/test_auth_service.py`
- `backend/tests/test_auth_schemas.py`
- `backend/tests/test_token_bearer_dependency.py`

Files modified:

- `backend/app/api/v1/endpoints/auth.py`
- `backend/app/schemas/auth.py`
- `backend/tests/conftest.py`

## Change Log

- 2025-12-20: Added login schemas + auth service + login endpoint + tests.
- 2025-12-20: Code review fixes: login returns 401 for any invalid password;
  added bearer-token dependency proof; normalized emails.

## Senior Developer Review (AI)

Date: 2025-12-20

Outcome: Approved (after fixes)

### Action Items

- [x] [HIGH] Login should return 401 for incorrect password even when password
      is short (avoid 422 schema rejection).
- [x] [HIGH] Provide evidence that returned token can authenticate subsequent
      requests via `Authorization: Bearer`.
- [x] [MEDIUM] Normalize emails (case/whitespace) for consistent uniqueness and
      login behavior.
