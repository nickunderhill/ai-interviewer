# Story 2.2: Implement Password Hashing with Bcrypt

Status: ready-for-dev

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

- [ ] Task 1: Add bcrypt hashing helpers (AC: #1)

  - [ ] Implement `hash_password` using passlib + bcrypt (12 rounds)
  - [ ] Implement `verify_password` helper
  - [ ] Ensure helpers are located in `backend/app/core/security.py`

- [ ] Task 2: Add unit tests for hashing (AC: #1)
  - [ ] Hashing produces non-empty hash
  - [ ] Verify returns True for correct password
  - [ ] Verify returns False for incorrect password

## Dev Notes

### Critical Architecture Requirements

- Passwords must never be stored or logged in plain text.
- Use passlib + bcrypt with 12 rounds (project standard).

### Technical Implementation Details

- Suggested files:
  - `backend/app/core/security.py`
  - `backend/tests/**/test_security.py`
- Keep functions pure (no DB access); endpoints/services call them.
