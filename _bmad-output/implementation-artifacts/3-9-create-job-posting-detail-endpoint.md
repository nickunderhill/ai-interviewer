# Story 3.9: Create Job Posting Detail Endpoint

Status: done

## Story

As a user, I want to view a specific job posting's complete details, so that I
can review the full description before starting an interview.

## Acceptance Criteria

1. **Given** I am authenticated and have created a job posting **When** I GET
   `/api/v1/job-postings/{id}` **Then** the system returns the complete job
   posting including description **And** if the job posting doesn't exist or
   belongs to another user, it returns 404 Not Found **And** all fields are
   returned (id, title, company, description, experience_level, tech_stack,
   created_at, updated_at)

## Tasks / Subtasks

- [x] Task 1: Implement job posting detail service (AC: #1)

  - [x] Add function to `backend/app/services/job_posting_service.py`
  - [x] Function:
        `get_job_posting_by_id(db: AsyncSession, job_posting_id: UUID, user_id: UUID) -> Optional[JobPosting]`
  - [x] Query job posting by id AND user_id (ensure ownership)
  - [x] Return JobPosting object or None if not found

- [x] Task 2: Implement GET /api/v1/job-postings/{id} endpoint (AC: #1)

  - [x] Add GET endpoint to `backend/app/api/v1/endpoints/job_postings.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call job posting service to retrieve detail
  - [x] Return 200 OK with complete job posting data if found
  - [x] Return 404 Not Found if job posting doesn't exist or belongs to another
        user

- [x] Task 3: Add endpoint tests (AC: #1)
  - [x] Test successful retrieval returns 200 with complete data (including
        description)
  - [x] Test 404 when job posting doesn't exist
  - [x] Test 404 when job posting belongs to another user (isolation)
  - [x] Test 401 for unauthenticated request

---

## Implementation Summary

**Status**: Completed on 2025-12-22

**Files Created**:

- `backend/tests/api/v1/test_job_postings_get.py` - 4 endpoint tests

**Files Modified**:

- `backend/app/services/job_posting_service.py` - Added get_job_posting_by_id()
- `backend/app/api/v1/endpoints/job_postings.py` - Added GET /{id} endpoint

**Tests**: 4/4 passing

- test_get_job_posting_success
- test_get_job_posting_not_found_returns_404
- test_get_job_posting_other_user_returns_404
- test_get_job_posting_unauthenticated_returns_401

**Key Features**:

- Returns full details including description field
- Enforces ownership check (id AND user_id)
- Returns 404 for both non-existent and unauthorized access

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- Authorization: User can only view THEIR OWN job postings
- RESTful pattern: GET /api/v1/job-postings/{id} (resource endpoint)
- 404 for ownership violation: Treat same as "not found" (don't leak existence)
- Complete data: Include description field (unlike list endpoint)

### Technical Implementation Details

**Suggested files:**

- `backend/app/services/job_posting_service.py` - Add detail function
- `backend/app/api/v1/endpoints/job_postings.py` - Add GET /{id} endpoint
- `backend/tests/api/v1/test_job_postings_detail.py` - Endpoint tests

**Service Layer:**

```python
async def get_job_posting_by_id(
    db: AsyncSession,
    job_posting_id: UUID,
    user_id: UUID
) -> Optional[JobPosting]:
    result = await db.execute(
        select(JobPosting)
        .where(
            JobPosting.id == job_posting_id,
            JobPosting.user_id == user_id
        )
    )
    return result.scalar_one_or_none()
```

**API Endpoint:**

```python
@router.get("/{job_posting_id}", response_model=JobPostingResponse)
async def get_job_posting(
    job_posting_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job_posting = await job_posting_service.get_job_posting_by_id(
        db, job_posting_id, current_user.id
    )
    if not job_posting:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job_posting
```

**Response Schema:**

- Uses JobPostingResponse schema from story 3.7
- Includes ALL fields: id, user_id, title, company, description,
  experience_level, tech_stack, created_at, updated_at
- Description field included (unlike list endpoint)

**Error Handling:**

- 404 Not Found: Job posting doesn't exist OR belongs to another user (security
  pattern)
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create job posting, retrieve it by id successfully
- Attempt retrieval with non-existent id (404)
- Create job posting for user A, authenticate as user B, attempt retrieval (404)
- Test with invalid UUID format (422 validation error)
- Test authentication requirements

### Dependencies

- Requires JobPosting model from story 3.6
- Requires job posting service from stories 3.7-3.8
- Requires authentication from Epic 2

### Authorization Pattern

- Query filters by BOTH id AND user_id
- Returns 404 for ownership violations (don't leak existence of other users'
  data)
- Security best practice: Don't reveal whether resource exists for other users

### List vs Detail Pattern

- **List endpoint (3.8):** Summary data, excludes description (lightweight)
- **Detail endpoint (3.9):** Complete data, includes description (comprehensive)
- Frontend: Use list for navigation, detail for full view

### Use Cases

- User reviewing job posting before creating interview session
- User editing job posting (need current data first)
- User verifying job posting details after creation

### Performance Considerations

- Single record retrieval - no performance concerns
- Composite query (id + user_id) uses primary key index
- Description field can be large (up to 10KB) - acceptable for single record

### User Experience Considerations

- Frontend should display all fields with proper formatting
- Consider showing "Last updated" timestamp
- Tech stack displayed as pills/tags
- Description with preserved formatting (line breaks)

### Security Considerations

- User isolation enforced via composite query (id AND user_id)
- 404 for ownership violations prevents information disclosure
- No additional authorization needed beyond authentication
- Job posting id in URL is UUID (not sequential integer, harder to guess)

### Future Considerations

- If interview sessions start showing job posting details, consider embedding
  this data
- May need caching if job postings accessed frequently
- Consider read-only view for job postings used in completed sessions
  (historical context)
