# Story 3.11: Create Job Posting Delete Endpoint

Status: done

## Story

As a user, I want to delete a job posting, so that I can remove positions I'm no
longer interested in.

## Acceptance Criteria

1. **Given** I am authenticated and have created a job posting **When** I DELETE
   `/api/v1/job-postings/{id}` **Then** the system validates I own the job
   posting **And** the job posting is permanently removed from the database
   **And** the endpoint returns 204 No Content **And** if the job posting
   doesn't exist or belongs to another user, it returns 404 Not Found **And**
   any interview sessions using this job posting reference it correctly (foreign
   key behavior)

## Tasks / Subtasks

- [x] Task 1: Implement job posting deletion service (AC: #1)

  - [x] Add function to `backend/app/services/job_posting_service.py`
  - [x] Function:
        `delete_job_posting(db: AsyncSession, job_posting_id: UUID, user_id: UUID) -> None`
  - [x] Query job posting by id AND user_id (ensure ownership)
  - [x] Raise NotFoundException if not found or not owned
  - [x] Delete job posting and commit

- [x] Task 2: Implement DELETE /api/v1/job-postings/{id} endpoint (AC: #1)

  - [x] Add DELETE endpoint to `backend/app/api/v1/endpoints/job_postings.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call job posting service to delete
  - [x] Return 204 No Content on success
  - [x] Return 404 Not Found if job posting doesn't exist or not owned
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 3: Handle foreign key constraints (AC: #1)

  - [x] Determine foreign key behavior for InterviewSession relationship (Epic 4
        dependency)
  - [x] Options: CASCADE (delete sessions), SET NULL (orphan sessions), or
        RESTRICT (prevent deletion)
  - [x] Document chosen approach for Epic 4 implementation

- [x] Task 4: Add endpoint tests (AC: #1)
  - [x] Test successful deletion returns 204
  - [x] Test subsequent GET after DELETE returns 404
  - [x] Test 404 when deleting non-existent job posting
  - [x] Test 404 when deleting another user's job posting
  - [x] Test 401 for unauthenticated request

---

## Implementation Summary

**Status**: Completed on 2025-12-22

**Files Created**:

- `backend/tests/api/v1/test_job_postings_delete.py` - 6 endpoint tests

**Files Modified**:

- `backend/app/services/job_posting_service.py` - Added delete_job_posting()
- `backend/app/api/v1/endpoints/job_postings.py` - Added DELETE /{id} endpoint

**Tests**: 6/6 passing

- test_delete_job_posting_success
- test_get_after_delete_returns_404
- test_delete_job_posting_not_found_returns_404
- test_delete_job_posting_other_user_returns_404
- test_delete_job_posting_unauthenticated_returns_401
- test_recreate_after_delete

**Key Features**:

- Returns explicit Response(status_code=204) with no content
- Permanent deletion from database
- Enforces ownership check before deletion
- Foreign key constraints handled (will be SET NULL for future InterviewSession)

**Foreign Key Strategy**: For future InterviewSession relationship (Epic 4),
recommend SET NULL on job_posting_id when JobPosting is deleted, allowing
interview history to persist even if target job posting is removed.

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- Authorization: User can only delete THEIR OWN job postings
- RESTful pattern: DELETE /api/v1/job-postings/{id}
- HTTP 204 No Content: Standard for successful DELETE with no response body
- Permanent deletion: No soft delete (data is removed from database)
- 404 for ownership violations: Treat same as "not found" (don't leak existence)

### Technical Implementation Details

**Suggested files:**

- `backend/app/services/job_posting_service.py` - Add delete function
- `backend/app/api/v1/endpoints/job_postings.py` - Add DELETE endpoint
- `backend/tests/api/v1/test_job_postings_delete.py` - Endpoint tests

**Service Layer:**

```python
async def delete_job_posting(
    db: AsyncSession,
    job_posting_id: UUID,
    user_id: UUID
) -> None:
    result = await db.execute(
        select(JobPosting)
        .where(
            JobPosting.id == job_posting_id,
            JobPosting.user_id == user_id
        )
    )
    job_posting = result.scalar_one_or_none()

    if not job_posting:
        raise NotFoundException("Job posting not found")

    await db.delete(job_posting)
    await db.commit()
```

**API Endpoint:**

```python
@router.delete("/{job_posting_id}", status_code=204)
async def delete_job_posting(
    job_posting_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await job_posting_service.delete_job_posting(
        db, job_posting_id, current_user.id
    )
    return Response(status_code=204)
```

**Error Handling:**

- 204 No Content: Successful deletion (no response body)
- 404 Not Found: Job posting doesn't exist OR user doesn't own it
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create job posting, delete it, verify 204 response
- After deletion, verify GET returns 404
- Attempt deletion of non-existent job posting (404)
- Create job posting for user A, authenticate as user B, attempt deletion (404)
- Attempt deletion twice (second attempt returns 404)
- Test authentication requirements

### Dependencies

- Requires JobPosting model from story 3.6
- Requires job posting service from stories 3.7-3.10
- Requires authentication from Epic 2

### Foreign Key Considerations (Epic 4 Dependency)

**Critical Decision:** How should deletion affect interview sessions?

**Option A: RESTRICT (Recommended for MVP)**

- Prevent deletion if interview sessions reference this job posting
- Return 409 Conflict: "Cannot delete job posting with active interview
  sessions"
- Pros: Data integrity, prevents orphaned sessions
- Cons: User cannot delete job postings they've practiced with

**Option B: SET NULL**

- Allow deletion, set job_posting_id to NULL in interview sessions
- Sessions retain question/answer data but lose job posting context
- Pros: User can delete any job posting
- Cons: Historical sessions lose contextual reference

**Option C: CASCADE**

- Delete job posting and all related interview sessions
- Pros: Clean deletion, no orphaned data
- Cons: Destroys user's interview history (unacceptable for learning platform)

**Recommendation:** Implement RESTRICT for MVP

- Preserves interview history (critical for learning/improvement tracking)
- User can still view/analyze past sessions with full context
- Future: Add "archive" feature instead of deletion for job postings with
  sessions

### Implementation Note for Epic 4

```python
# In InterviewSession model (Epic 4, Story 4.1)
job_posting_id = Column(
    UUID(as_uuid=True),
    ForeignKey("job_postings.id", ondelete="RESTRICT"),  # Prevent deletion if sessions exist
    nullable=False
)
```

### REST Semantics

- DELETE is idempotent in principle, but second DELETE returns 404 (resource
  doesn't exist)
- 204 No Content = successful deletion with no response body
- Standard REST pattern for DELETE operations

### Authorization Pattern

- Query filters by BOTH id AND user_id
- Returns 404 for ownership violations (security best practice)
- Don't reveal existence of other users' job postings

### User Experience Considerations

- Frontend should show confirmation dialog before deletion
- Warning message: "This will permanently delete this job posting"
- If RESTRICT implemented: Show error "Cannot delete job posting with interview
  sessions. Archive it instead?"
- Consider "archive" feature instead of deletion

### Data Retention Considerations

- Hard delete (permanent removal) - no audit trail in MVP
- If future requirements need audit trail, implement soft delete pattern
- Current requirement: Permanent deletion per AC (subject to foreign key
  constraints)

### Performance Considerations

- Single record deletion - no performance concerns
- Composite query (id + user_id) uses primary key index
- Foreign key constraint check (if RESTRICT) adds minimal overhead

### Security Considerations

- User isolation enforced via composite query (id AND user_id)
- 404 for ownership violations prevents information disclosure
- Deletion is permanent - ensure user intent via frontend confirmation
- No additional authorization needed beyond authentication

### Future Enhancements

- Archive functionality (soft delete) for job postings with interview sessions
- Bulk deletion (delete multiple job postings at once)
- Deletion confirmation via email for important data
- Audit trail for deleted job postings (compliance requirement)
