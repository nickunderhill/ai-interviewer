# Story 2.6: Implement Authentication Middleware with JWT

Status: ready-for-dev

## Story

As a developer, I want to create a dependency that validates JWT tokens on
protected endpoints, so that only authenticated users can access their data.

## Acceptance Criteria

1. **Given** JWT token functions are implemented **When** I create a
   `get_current_user` dependency in app/core/dependencies.py **Then** the
   dependency extracts the JWT token from the Authorization header **And** the
   token is validated and decoded to get the user_id **And** the user is loaded
   from the database and returned **And** missing token returns 401 Unauthorized
   **And** invalid token returns 401 Unauthorized **And** expired token returns
   401 Unauthorized **And** protected endpoints can use this dependency to
   require authentication

## Tasks / Subtasks

- [ ] Task 1: Implement `get_current_user` dependency (AC: #1)

  - [ ] Extract bearer token from Authorization header
  - [ ] Decode/validate token (reject expired/invalid)
  - [ ] Load user from DB using async SQLAlchemy
  - [ ] Return user object (or user schema depending on pattern)

- [ ] Task 2: Standardize auth error responses (AC: #1)

  - [ ] 401 on missing/invalid/expired token
  - [ ] Ensure error format matches project conventions

- [ ] Task 3: Add tests for protected routes (AC: #1)
  - [ ] Missing token returns 401
  - [ ] Invalid token returns 401
  - [ ] Valid token authenticates

## Dev Notes

### Critical Architecture Requirements

- Protected routes must use `get_current_user` dependency.
- JWT must be supplied via `Authorization: Bearer {token}`.
- Database access must use async SQLAlchemy (`AsyncSession`).

### Technical Implementation Details

- Suggested files:
  - `backend/app/core/dependencies.py`
  - `backend/app/core/security.py`
  - `backend/tests/api/v1/test_auth_dependency.py`
