# Story 2.11: Create API Key Update Endpoint

Status: ready-for-dev

## Story

As a user, I want to update my stored OpenAI API key, so that I can change it if
needed.

## Acceptance Criteria

1. **Given** I am authenticated and have previously stored an API key **When** I
   PUT to `/api/v1/users/me/api-key` with a new API key **Then** the new API key
   is encrypted and replaces the old encrypted key **And** the endpoint returns
   200 OK with a success message **And** subsequent AI operations use the new
   API key **And** the old API key is overwritten and no longer accessible

## Tasks / Subtasks

- [ ] Task 1: Add/Reuse schemas for update (AC: #1)

  - [ ] Request schema with `api_key`
  - [ ] Response schema with success message

- [ ] Task 2: Implement PUT endpoint (AC: #1)

  - [ ] Protect route with `get_current_user`
  - [ ] Require existing key present (decide whether to return 404 or 409 if
        missing)
  - [ ] Encrypt new key and overwrite `encrypted_api_key`

- [ ] Task 3: Add endpoint tests (AC: #1)
  - [ ] Requires auth (401 if missing)
  - [ ] Overwrites existing encrypted key
  - [ ] Response does not contain API key

## Dev Notes

### Critical Architecture Requirements

- API keys are sensitive; never return them in responses.
- Replacement must overwrite prior encrypted key (no history stored in MVP).

### Technical Implementation Details

- Suggested files:
  - `backend/app/api/v1/endpoints/users.py`
  - `backend/app/services/user_service.py`
  - `backend/tests/api/v1/test_users_api_key_put.py`
