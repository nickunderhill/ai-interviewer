# Story 3.3: Create Resume Viewing Endpoint

Status: done

## Story

As a user, I want to view my stored résumé, so that I can verify the content is
correct.

## Acceptance Criteria

1. **Given** I am authenticated and have uploaded a résumé **When** I GET
   `/api/v1/resumes/me` **Then** the system returns my résumé content with
   metadata (id, created_at, updated_at) **And** if I don't have a résumé, it
   returns 404 Not Found **And** other users cannot access my résumé (enforced
   by authentication)

## Tasks / Subtasks

- [x] Task 1: Implement resume retrieval service (AC: #1)

  - [x] Add function to `backend/app/services/resume_service.py`
  - [x] Function:
        `get_user_resume(db: AsyncSession, user_id: UUID) -> Optional[Resume]`
  - [x] Query resume by user_id
  - [x] Return Resume object or None if not found

- [x] Task 2: Implement GET /api/v1/resumes/me endpoint (AC: #1)

  - [x] Add GET endpoint to `backend/app/api/v1/endpoints/resumes.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call resume service to retrieve resume
  - [x] Return 200 OK with resume data if found
  - [x] Return 404 Not Found if user has no resume
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 3: Add endpoint tests (AC: #1)
  - [x] Test successful retrieval returns 200 with resume data
  - [x] Test 404 when user has no resume
  - [x] Test 401 for unauthenticated request
  - [x] Test user can only access their own resume (isolation)

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- User isolation: User can only retrieve THEIR OWN resume (via user_id from
  token)
- RESTful pattern: GET /api/v1/resumes/me (using "me" as current user
  identifier)
- 404 Not Found: When user has no resume (not an error, just no data)

### Technical Implementation Details

**Suggested files:**

- `backend/app/services/resume_service.py` - Service function (add to existing)
- `backend/app/api/v1/endpoints/resumes.py` - API endpoint (add to existing)
- `backend/tests/api/v1/test_resumes_get.py` - Endpoint tests

**Service Layer:**

```python
async def get_user_resume(
    db: AsyncSession,
    user_id: UUID
) -> Optional[Resume]:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id)
    )
    return result.scalar_one_or_none()
```

**API Endpoint:**

```python
@router.get("/me", response_model=ResumeResponse)
async def get_my_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    resume = await resume_service.get_user_resume(db, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume
```

**Response Schema:**

- Uses ResumeResponse schema from story 3.2
- Includes: id, user_id, content, created_at, updated_at
- Content is returned in full (no truncation)

**Error Handling:**

- 404 Not Found: User has no resume (expected case, not an error)
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create resume, then retrieve it successfully
- Attempt retrieval without creating resume (404)
- Create resume for user A, authenticate as user B, verify cannot access user
  A's resume
- Test with invalid token (401)
- Test with expired token (401)

### Dependencies

- Requires Resume model from story 3.1
- Requires resume service from story 3.2
- Requires authentication from Epic 2

### User Experience Considerations

- Frontend should handle 404 gracefully (show "No resume uploaded" message)
- Resume content displayed with proper formatting (preserve line breaks)
- Consider showing resume metadata (upload date, last updated)

### Performance Considerations

- Resume content can be large (up to 50KB) - acceptable for single-record
  retrieval
- No pagination needed (one-to-one relationship with user)
- Query indexed on user_id (foreign key automatically indexed)

### Security Considerations

- User isolation enforced via authentication and user_id filtering
- No additional authorization needed (user can always access their own resume)
- Resume content may contain PII - ensure HTTPS in production

## Dev Agent Record

✅ Story 3.3 complete - GET /api/v1/resumes/me endpoint implemented with 4 tests
passing

## File List

Modified:

- backend/app/services/resume_service.py (added get_user_resume)
- backend/app/api/v1/endpoints/resumes.py (added GET /me endpoint)

Created:

- backend/tests/api/v1/test_resumes_get.py

## Change Log

- 2025-12-22 14:30: Code review fixes - added service layer tests for
  get_user_resume()
- 2025-12-22: Implemented GET endpoint for resume retrieval with user isolation
  tests
