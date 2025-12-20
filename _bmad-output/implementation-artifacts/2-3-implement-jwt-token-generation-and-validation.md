# Story 2.3: Implement JWT Token Generation and Validation

Status: ready-for-dev

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

- [ ] Task 1: Implement JWT helpers (AC: #1)

  - [ ] Add `create_access_token` with 24h expiry
  - [ ] Add `decode_access_token` that validates signature + exp
  - [ ] Load `SECRET_KEY` from environment/config
  - [ ] Use HS256

- [ ] Task 2: Add unit tests for tokens (AC: #1)
  - [ ] Token contains `user_id` claim
  - [ ] Expired token is rejected
  - [ ] Invalid signature is rejected

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
