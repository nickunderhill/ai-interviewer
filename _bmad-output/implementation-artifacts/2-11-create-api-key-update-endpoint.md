# Story 2.11: Create API Key Update Endpoint

Status: done

## Story

As a user, I want to update my stored OpenAI API key, so that I can change it if
needed.

## Acceptance Criteria

1. **Given** I am authenticated and have previously stored an API key **When** I
   PUT to `/api/v1/users/me/api-key` with a new API key **Then** the new API key
   is encrypted and replaces the old encrypted key **And** the endpoint returns
   200 OK with a success message **And** subsequent AI operations use the new
   API key (deferred to Epic 4 - OpenAI integration) **And** the old API key is
   overwritten and no longer accessible

## Tasks / Subtasks

- [x] Task 1: Add/Reuse schemas for update (AC: #1)

  - [x] Request schema with `api_key`
  - [x] Response schema with success message

- [x] Task 2: Implement PUT endpoint (AC: #1)

  - [x] Protect route with `get_current_user`
  - [x] Allow updating even when no existing key (works for both create and
        update)
  - [x] Encrypt new key and overwrite `encrypted_api_key`

- [x] Task 3: Add endpoint tests (AC: #1)
  - [x] Requires auth (401 if missing)
  - [x] Overwrites existing encrypted key
  - [x] Response does not contain API key

## Dev Notes

### Critical Architecture Requirements

- API keys are sensitive; never return them in responses.
- Replacement must overwrite prior encrypted key (no history stored in MVP).

### Technical Implementation Details

Implementation files:

- `backend/app/api/v1/endpoints/users.py` - PUT endpoint implementation
- `backend/tests/api/v1/test_users_api_key_put.py` - Endpoint tests
- Note: Service layer not needed - logic placed directly in endpoint for
  simplicity

## Dev Agent Record

### File List

**Created Files:**

- `backend/tests/api/v1/test_users_api_key_put.py` - 7 comprehensive tests for
  PUT endpoint

**Modified Files:**

- `backend/app/api/v1/endpoints/users.py` - Added PUT `/api/v1/users/me/api-key`
  endpoint (lines 76-109)
- `_bmad-output/implementation-artifacts/2-11-create-api-key-update-endpoint.md` -
  Updated status and tasks
- `_bmad-output/implementation-artifacts/sprint-status.yaml` - Updated story
  status to done

**Reused Files (from previous stories):**

- `backend/app/schemas/api_key.py` - Reused ApiKeySetRequest and
  ApiKeySetResponse
- `backend/app/core/dependencies.py` - Used get_current_user for authentication
- `backend/app/services/encryption_service.py` - Used encrypt_api_key function
- `backend/app/models/user.py` - Used User.encrypted_api_key field

### Change Log

**2025-12-21 - Story 2.11 Implementation**

1. **RED Phase (TDD)**

   - Created `test_users_api_key_put.py` with 7 test cases
   - Tests verify: authentication, key overwriting, encryption, validation
   - Confirmed tests fail (405 Method Not Allowed)

2. **GREEN Phase**

   - Implemented PUT `/api/v1/users/me/api-key` endpoint in `users.py`
   - Reused schemas from Story 2.10 (ApiKeySetRequest, ApiKeySetResponse)
   - Protected with get_current_user dependency
   - Encrypts API key before storage
   - Overwrites existing key (works for both create and update scenarios)

3. **Validation**

   - All 7 PUT endpoint tests passing
   - 118 total async tests passing (no regressions)
   - 87% code coverage maintained
   - Verified encryption, authentication, and security requirements

4. **Documentation Updates**
   - Updated story status to "review"
   - Updated sprint status to "done"
   - Marked all tasks complete
   - Clarified AC note about AI operations (deferred to Epic 4)

### Test Results

```
7/7 tests passing for PUT endpoint
118/118 total async tests passing
87% code coverage
0 regressions
```

**Test Coverage:**

- ✅ Requires authentication (401 without token)
- ✅ Rejects invalid tokens (401)
- ✅ Overwrites existing encrypted key
- ✅ Never returns API key in response
- ✅ Works when no existing key present
- ✅ Rejects empty string API keys (422)
- ✅ Stores encrypted value, not plaintext
  - `backend/tests/api/v1/test_users_api_key_put.py`
