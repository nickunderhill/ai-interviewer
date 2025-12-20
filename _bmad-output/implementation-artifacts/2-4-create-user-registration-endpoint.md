# Story 2.4: Create User Registration Endpoint

Status: ready-for-dev

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

- [ ] Task 1: Add request/response schemas (AC: #1)

  - [ ] Create Pydantic request schema (email, password)
  - [ ] Create Pydantic response schema (id, email, created_at)

- [ ] Task 2: Implement registration endpoint (AC: #1)

  - [ ] Add route handler under `backend/app/api/v1/endpoints/` (auth)
  - [ ] Enforce unique email (409 on conflict)
  - [ ] Hash password before insert
  - [ ] Return 201 with user data excluding password hash

- [ ] Task 3: Add endpoint tests (AC: #1)
  - [ ] Successful registration
  - [ ] Duplicate email returns 409
  - [ ] Invalid email returns 422

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
