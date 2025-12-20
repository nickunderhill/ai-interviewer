# Story 2.10: Create API Key Configuration Endpoint

Status: ready-for-dev

## Story

As a user, I want to securely configure and store my OpenAI API key, so that the
system can make AI-powered interview calls on my behalf.

## Acceptance Criteria

1. **Given** I am authenticated **When** I POST to `/api/v1/users/me/api-key`
   with my OpenAI API key **Then** the API key is encrypted using AES-256 before
   storage **And** the encrypted key is stored in the encrypted_api_key field
   **And** the endpoint returns 200 OK with a success message **And** the plain
   text API key is never stored in the database **And** the API key is never
   included in any response **And** unauthenticated requests return 401
   Unauthorized

## Tasks / Subtasks

- [ ] Task 1: Add request/response schemas (AC: #1)

  - [ ] Request schema with `api_key` field
  - [ ] Response schema with success message only

- [ ] Task 2: Implement POST endpoint (AC: #1)

  - [ ] Protect route with `get_current_user`
  - [ ] Encrypt key using encryption service
  - [ ] Store encrypted value in `users.encrypted_api_key`
  - [ ] Ensure no response includes API key

- [ ] Task 3: Add endpoint tests (AC: #1)
  - [ ] Unauthenticated call returns 401
  - [ ] Successful set stores encrypted value (not plain text)
  - [ ] Response does not contain API key

## Dev Notes

### Critical Architecture Requirements

- API keys must never be exposed to frontend or returned in API responses.
- Backend acts as the proxy for all OpenAI calls using stored encrypted key.

### Technical Implementation Details

- Suggested files:
  - `backend/app/api/v1/endpoints/users.py`
  - `backend/app/schemas/users_api_key.py` (or `users.py`)
  - `backend/app/services/user_service.py`
  - `backend/tests/api/v1/test_users_api_key_post.py`
