# Story 2.3: Implement JWT Token Generation and Validation

Status: done

## Story

As a developer, I want to implement JWT token generation and validation for
stateless authentication, so that users can securely authenticate API requests.

## Acceptance Criteria

1. **Given** python-jose is installed **When** I create JWT functions in
   app/core/security.py **Then** a `create_access_token(data: dict) -> str`
   function generates JWT tokens **And** tokens include user_id and expiration
   time (24 hours from creation) **And** a
   `decode_access_token(token: str) -> dict` function validates and decodes
   tokens **And** expired tokens are rejected with appropriate error **And**
   tokens are signed with a SECRET_KEY from environment variables **And** the
   implementation uses HS256 algorithm

## Tasks / Subtasks

- [x] Task 1: Implement JWT helpers (AC: #1)

  - [x] Add `create_access_token` with 24h expiry
  - [x] Add `decode_access_token` that validates signature + exp
  - [x] Load `SECRET_KEY` from environment/config
  - [x] Use HS256

- [x] Task 2: Add unit tests for tokens (AC: #1)
  - [x] Token contains `user_id` claim
  - [x] Expired token is rejected
  - [x] Invalid signature is rejected

## Dev Notes

### Critical Architecture Requirements

- Auth is JWT-based and stateless.
- Token must be supplied via `Authorization: Bearer {token}`.
- Secret must come from environment (never hard-coded).

### Technical Implementation Details

- Suggested files:
  - `backend/app/core/security.py`
  - `backend/app/core/config.py` (or existing settings module)
  - `backend/tests/**/test_security_jwt.py`

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Implementation Notes

- Confirmed JWT helpers are implemented in `backend/app/core/security.py` using
  `settings.SECRET_KEY` and HS256.
- Token expiry is set via `settings.ACCESS_TOKEN_EXPIRE_MINUTES` (default 24h)
  and enforced during decode.

### Test Results

- `DB_HOST=localhost pytest -q` (79 passed)

## File List

Files created:

- `backend/tests/test_security_jwt.py`

Files modified:

- `backend/app/core/security.py`
- `backend/tests/conftest.py`

## Change Log

- 2025-12-20: Added JWT unit tests for user_id claim, expiry rejection, and
  invalid signature rejection.
- 2025-12-20: Code review fixes: enforce `user_id` at token creation, enforce
  HS256 + 24h expiry, and strengthen JWT tests.

## Senior Developer Review (AI)

**Date:** 2025-12-20

**Outcome:** Approved (changes applied)

**Findings addressed:**

- HIGH: Enforced `user_id` presence at token creation to match AC.
- MEDIUM: Enforced HS256 + ~24h expiry via tests; added missing-user_id test.
