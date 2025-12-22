# Story 3.4: Create Resume Update Endpoint

Status: done

## Story

As a user, I want to edit my stored résumé, so that I can keep my information up
to date.

## Acceptance Criteria

1. **Given** I am authenticated and have a résumé **When** I PUT to
   `/api/v1/resumes/me` with updated content **Then** my existing résumé content
   is replaced with the new content **And** the updated_at timestamp is updated
   **And** the endpoint returns 200 OK with the updated résumé **And** if I
   don't have a résumé, it returns 404 Not Found

## Tasks / Subtasks

- [x] Task 1: Create update schema (AC: #1)

  - [x] Add ResumeUpdate schema to `backend/app/schemas/resume.py`
  - [x] Same validation as ResumeCreate (content: str, min_length=1,
        max_length=50000)

- [x] Task 2: Implement resume update service (AC: #1)

  - [x] Add function to `backend/app/services/resume_service.py`
  - [x] Function:
        `update_user_resume(db: AsyncSession, user_id: UUID, content: str) -> Resume`
  - [x] Query resume by user_id
  - [x] Raise NotFoundException if resume doesn't exist
  - [x] Update content field and updated_at timestamp
  - [x] Commit and return updated Resume

- [x] Task 3: Implement PUT /api/v1/resumes/me endpoint (AC: #1)

  - [x] Add PUT endpoint to `backend/app/api/v1/endpoints/resumes.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call resume service to update resume
  - [x] Return 200 OK with updated resume data
  - [x] Return 404 Not Found if user has no resume
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 4: Add endpoint tests (AC: #1)
  - [x] Test successful update returns 200 with updated content
  - [x] Test updated_at timestamp changes after update
  - [x] Test 404 when updating non-existent resume
  - [x] Test 422 for invalid content (empty, too long)
  - [x] Test 401 for unauthenticated request

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- RESTful pattern: PUT /api/v1/resumes/me (full replacement, not partial update)
- Automatic timestamp update: updated_at should reflect modification time
- 404 for missing resume: Cannot update what doesn't exist
- Content validation: Same rules as creation (not empty, max 50KB)

### Technical Implementation Details

**Suggested files:**

- `backend/app/schemas/resume.py` - Add ResumeUpdate schema
- `backend/app/services/resume_service.py` - Add update function
- `backend/app/api/v1/endpoints/resumes.py` - Add PUT endpoint
- `backend/tests/api/v1/test_resumes_put.py` - Endpoint tests

**Pydantic Schema:**

```python
class ResumeUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)
```

**Service Layer:**

```python
async def update_user_resume(
    db: AsyncSession,
    user_id: UUID,
    content: str
) -> Resume:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise NotFoundException("Resume not found")

    resume.content = content
    resume.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(resume)
    return resume
```

**API Endpoint:**

```python
@router.put("/me", response_model=ResumeResponse)
async def update_my_resume(
    resume_data: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    resume = await resume_service.update_user_resume(
        db, current_user.id, resume_data.content
    )
    return resume
```

**Error Handling:**

- 404 Not Found: User has no resume to update
- 422 Validation Error: Empty content or exceeds max length
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create resume, then update it, verify content and updated_at changed
- Attempt update without creating resume first (404)
- Update with invalid content (empty, too long)
- Verify id and created_at remain unchanged
- Test authentication requirements

### Dependencies

- Requires Resume model from story 3.1
- Requires resume service from stories 3.2-3.3
- Requires authentication from Epic 2

### Timestamp Behavior

- **created_at:** NEVER changes (records original creation time)
- **updated_at:** ALWAYS updated on modification
- Both timestamps use UTC timezone

### REST Semantics

- PUT = Full replacement (entire content replaced)
- If partial updates needed in future, use PATCH
- Current implementation: Full content replacement only

### User Experience Considerations

- Frontend should show "last updated" timestamp
- Consider showing "unsaved changes" indicator before PUT request
- Optimistic UI update recommended (update UI before server response)

### Performance Considerations

- Single record update - no performance concerns
- Content validation on server side prevents large payloads
- Updated_at timestamp automatically handled by SQLAlchemy or explicit update

### Security Considerations

- User can only update their own resume (enforced via user_id from token)
- Content validation prevents malicious large payloads
- No additional authorization needed beyond authentication

## Dev Agent Record

✅ Story 3.4 complete - PUT /api/v1/resumes/me endpoint with automatic timestamp
updates, 6 tests passing

## File List

Modified:

- backend/app/schemas/resume.py (added ResumeUpdate)
- backend/app/services/resume_service.py (added update_user_resume)
- backend/app/api/v1/endpoints/resumes.py (added PUT /me endpoint)

Created:

- backend/tests/api/v1/test_resumes_put.py

## Change Log

- 2025-12-22 14:30: Code review fixes - added explicit updated_at timestamp
  update in service, added service layer tests, improved timestamp test (removed
  sleep)
- 2025-12-22: Implemented PUT endpoint for full content replacement with
  validation
