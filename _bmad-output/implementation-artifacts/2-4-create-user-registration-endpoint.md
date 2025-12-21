# Story 2.4: Create User Registration Endpoint

Status: done

## Story

As a user, I want to register for an account with my email and password, so that
I can access the AI interview system.

## Acceptance Criteria

1. **Given** the User model and password hashing are implemented **When** I POST
   to `/api/v1/auth/register` with email and password **Then** the system
   validates that the email is unique **And** the password is hashed using
   bcrypt before storage **And** a new user record is created in the database
   **And** the endpoint returns 201 Created with user data (excluding password)
   **And** attempting to register with a duplicate email returns 409 Conflict
   **And** invalid email format returns 422 Validation Error

## Tasks / Subtasks

- [x] Task 1: Add request/response schemas (AC: #1)

  - [x] Create Pydantic request schema (email, password)
  - [x] Create Pydantic response schema (id, email, created_at)

- [x] Task 2: Implement registration endpoint (AC: #1)

  - [x] Add route handler under `backend/app/api/v1/endpoints/` (auth)
  - [x] Enforce unique email (409 on conflict)
  - [x] Hash password before insert
  - [x] Return 201 with user data excluding password hash

- [x] Task 3: Add endpoint tests (AC: #1)
  - [x] Successful registration
  - [x] Duplicate email returns 409
  - [x] Invalid email returns 422

## Dev Notes

### Critical Architecture Requirements

- API base path is `/api/v1/`.
- Error shape should follow project pattern:
  `{"detail": {"code": "ERROR_CODE", "message": "..."}}`.
- Never return password hash in API responses.

### Technical Implementation Details

- Suggested files:
  - `backend/app/api/v1/endpoints/auth.py`
  - `backend/app/schemas/auth.py` (or `users.py` depending on existing layout)
  - `backend/app/services/user_service.py`
  - `backend/tests/api/v1/test_auth_register.py`

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Implementation Notes

- Added `/api/v1/auth/register` endpoint that hashes passwords with bcrypt and
  returns user data without the password hash.
- Returns 409 on duplicate email using the project error shape.

### Test Results

- `pytest -q` (96 passed)

## File List

Files created:

- `backend/app/api/v1/endpoints/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/user_service.py`
- `backend/tests/api/v1/test_auth_register.py`

Files modified:

- `backend/app/main.py`
- `backend/app/services/user_service.py`
- `backend/tests/api/v1/test_auth_register.py`
- `backend/tests/conftest.py`

## Change Log

- 2025-12-20: Added registration endpoint + schemas + service + tests.
- 2025-12-21: Code review fixes: added DB assertions for hashing + email
  normalization behavior; updated story metadata.

## Senior Developer Review (AI)

Date: 2025-12-21

Outcome: Approved (after fixes)

### Action Items

- [x] [MEDIUM] Add test coverage proving password is hashed in DB (not just
      omitted from response).
- [x] [MEDIUM] Add test coverage for email normalization and case-insensitive
      uniqueness.
- [x] [MEDIUM] Keep story File List and test counts consistent with repo
      changes.
