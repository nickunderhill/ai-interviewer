# Story 3.5: Create Resume Delete Endpoint

Status: done

## Story

As a user, I want to delete my résumé, so that I can remove my information from
the system.

## Acceptance Criteria

1. **Given** I am authenticated and have a résumé **When** I DELETE
   `/api/v1/resumes/me` **Then** my résumé is permanently removed from the
   database **And** the endpoint returns 204 No Content **And** subsequent GET
   requests return 404 Not Found **And** if I don't have a résumé, it returns
   404 Not Found

## Tasks / Subtasks

- [x] Task 1: Implement resume deletion service (AC: #1)

  - [x] Add function to `backend/app/services/resume_service.py`
  - [x] Function: `delete_user_resume(db: AsyncSession, user_id: UUID) -> None`
  - [x] Query resume by user_id
  - [x] Raise NotFoundException if resume doesn't exist
  - [x] Delete resume and commit

- [x] Task 2: Implement DELETE /api/v1/resumes/me endpoint (AC: #1)

  - [x] Add DELETE endpoint to `backend/app/api/v1/endpoints/resumes.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call resume service to delete resume
  - [x] Return 204 No Content on success
  - [x] Return 404 Not Found if user has no resume
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 3: Add endpoint tests (AC: #1)
  - [x] Test successful deletion returns 204
  - [x] Test subsequent GET after DELETE returns 404
  - [x] Test 404 when deleting non-existent resume
  - [x] Test 401 for unauthenticated request
  - [x] Test cascade implications (if any related data exists)

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- RESTful pattern: DELETE /api/v1/resumes/me
- HTTP 204 No Content: Standard for successful DELETE with no response body
- Permanent deletion: No soft delete, data is removed from database
- 404 for missing resume: Cannot delete what doesn't exist

### Technical Implementation Details

**Suggested files:**

- `backend/app/services/resume_service.py` - Add delete function
- `backend/app/api/v1/endpoints/resumes.py` - Add DELETE endpoint
- `backend/tests/api/v1/test_resumes_delete.py` - Endpoint tests

**Service Layer:**

```python
async def delete_user_resume(
    db: AsyncSession,
    user_id: UUID
) -> None:
    result = await db.execute(
        select(Resume).where(Resume.user_id == user_id)
    )
    resume = result.scalar_one_or_none()

    if not resume:
        raise NotFoundException("Resume not found")

    await db.delete(resume)
    await db.commit()
```

**API Endpoint:**

```python
@router.delete("/me", status_code=204)
async def delete_my_resume(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await resume_service.delete_user_resume(db, current_user.id)
    return Response(status_code=204)
```

**Error Handling:**

- 204 No Content: Successful deletion (no response body)
- 404 Not Found: User has no resume to delete
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create resume, delete it, verify 204 response
- After deletion, verify GET returns 404
- Attempt to delete non-existent resume (404)
- Attempt to delete twice (second attempt returns 404)
- Test authentication requirements

### Dependencies

- Requires Resume model from story 3.1
- Requires resume service from stories 3.2-3.4
- Requires authentication from Epic 2

### Cascade Considerations

- Resume has one-to-one relationship with User
- If User is deleted, Resume is cascaded (CASCADE configured in story 3.1)
- Resume deletion does NOT affect User (no reverse cascade)
- Future consideration: If interview sessions reference resume, need to handle
  orphaned sessions

### REST Semantics

- DELETE is idempotent in principle, but second DELETE returns 404 (resource
  doesn't exist)
- 204 No Content = successful deletion with no response body
- Some APIs return 200 OK with deleted object - we follow 204 pattern per REST
  standards

### User Experience Considerations

- Frontend should show confirmation dialog before deletion ("Are you sure?")
- After deletion, redirect to resume upload page or show "No resume" state
- Consider showing success message after 204 response
- Cannot undo deletion - warn user about permanence

### Data Retention Considerations

- Hard delete (permanent removal) - no audit trail
- If future requirements need audit trail, implement soft delete pattern
- Current requirement: Permanent deletion per AC

### Security Considerations

- User can only delete their own resume (enforced via user_id from token)
- No additional authorization needed beyond authentication
- Deletion is permanent - ensure user intent via frontend confirmation

### Future Considerations

- If interview sessions start referencing resume content (not just user), need
  to:
  - Either prevent deletion if sessions exist
  - Or handle orphaned session references
  - Current Epic 3 scope: No session dependency yet

## Dev Agent Record

✅ Story 3.5 complete - DELETE /api/v1/resumes/me endpoint with permanent
deletion, 5 tests passing including recreate-after-delete

## File List

Modified:

- backend/app/services/resume_service.py (added delete_user_resume with
  ResumeNotFoundException)
- backend/app/api/v1/endpoints/resumes.py (added DELETE /me endpoint
  returning 204)

Created:

- backend/tests/api/v1/test_resumes_delete.py

## Change Log

- 2025-12-22 14:30: Code review fixes - explicit Response(status_code=204)
  return, added service layer tests, documented empty migration
- 2025-12-22: Implemented DELETE endpoint for permanent resume removal with 204
  No Content response
