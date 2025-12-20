# Story 2.2: Implement Password Hashing with Bcrypt

Status: done

## Story

As a developer, I want to implement secure password hashing using bcrypt with 12
rounds, so that user passwords are never stored in plain text.

## Acceptance Criteria

1. **Given** passlib with bcrypt is installed **When** I create password hashing
   functions in app/core/security.py **Then** a
   `hash_password(password: str) -> str` function uses bcrypt with 12 rounds
   **And** a
   `verify_password(plain_password: str, hashed_password: str) -> bool` function
   verifies passwords **And** the hashed passwords are never reversible to plain
   text **And** password verification returns True for correct passwords and
   False for incorrect ones

## Tasks / Subtasks

- [x] Task 1: Add bcrypt hashing helpers (AC: #1)

  - [x] Implement `hash_password` using passlib + bcrypt (12 rounds)
  - [x] Implement `verify_password` helper
  - [x] Ensure helpers are located in `backend/app/core/security.py`

- [x] Task 2: Add unit tests for hashing (AC: #1)
  - [x] Hashing produces non-empty hash
  - [x] Verify returns True for correct password
  - [x] Verify returns False for incorrect password

## Dev Notes

### Critical Architecture Requirements

- Passwords must never be stored or logged in plain text.
- Use passlib + bcrypt with 12 rounds (project standard).

### Technical Implementation Details

- Suggested files:
  - `backend/app/core/security.py`
  - `backend/tests/**/test_security.py`
- Keep functions pure (no DB access); endpoints/services call them.

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Implementation Notes

- Added bcrypt password hashing and verification helpers using passlib with 12
  rounds.
- Kept helpers pure (no DB access) and safe-failing on invalid hashes.

### Test Results

- `DB_HOST=localhost pytest -q` (79 passed)

## File List

Files created:

- `backend/app/core/security.py`
- `backend/tests/test_security.py`

Files modified:

- `backend/tests/conftest.py`

## Change Log

- 2025-12-20: Added bcrypt password hashing helpers + unit tests.
- 2025-12-20: Code review fixes: assert bcrypt cost=12, add invalid-hash test,
  and make tests resilient to missing `SECRET_KEY`.

## Senior Developer Review (AI)

**Date:** 2025-12-20

**Outcome:** Approved (changes applied)

**Findings addressed:**

- HIGH: N/A for 2.2
- MEDIUM: Added tests to enforce bcrypt cost factor and invalid-hash behavior.
