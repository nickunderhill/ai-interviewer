# Story 3.10: Create Job Posting Update Endpoint

Status: done

## Story

As a user, I want to edit an existing job posting, so that I can correct or
update the job information.

## Acceptance Criteria

1. **Given** I am authenticated and have created a job posting **When** I PUT to
   `/api/v1/job-postings/{id}` with updated data **Then** the system validates I
   own the job posting **And** the specified fields are updated (title, company,
   description, experience_level, tech_stack) **And** the updated_at timestamp
   is updated **And** the endpoint returns 200 OK with the updated job posting
   **And** if the job posting doesn't exist or belongs to another user, it
   returns 404 Not Found

## Tasks / Subtasks

- [x] Task 1: Create update schema (AC: #1)

  - [x] Add JobPostingUpdate schema to `backend/app/schemas/job_posting.py`
  - [x] Include all updatable fields: title, company, description,
        experience_level, tech_stack
  - [x] Same validation as JobPostingCreate

- [x] Task 2: Implement job posting update service (AC: #1)

  - [x] Add function to `backend/app/services/job_posting_service.py`
  - [x] Function:
        `update_job_posting(db: AsyncSession, job_posting_id: UUID, user_id: UUID, data: JobPostingUpdate) -> JobPosting`
  - [x] Query job posting by id AND user_id (ensure ownership)
  - [x] Raise NotFoundException if not found or not owned
  - [x] Update all fields from data
  - [x] Update updated_at timestamp
  - [x] Commit and return updated JobPosting

- [x] Task 3: Implement PUT /api/v1/job-postings/{id} endpoint (AC: #1)

  - [x] Add PUT endpoint to `backend/app/api/v1/endpoints/job_postings.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call job posting service to update
  - [x] Return 200 OK with updated job posting data
  - [x] Return 404 Not Found if job posting doesn't exist or not owned
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 4: Add endpoint tests (AC: #1)
  - [x] Test successful update returns 200 with updated data
  - [x] Test updated_at timestamp changes after update
  - [x] Test 404 when updating non-existent job posting
  - [x] Test 404 when updating another user's job posting
  - [x] Test 422 for invalid data (missing required fields)
  - [x] Test 401 for unauthenticated request

---

## Implementation Summary

**Status**: Completed on 2025-12-22

**Files Created**:

- `backend/tests/api/v1/test_job_postings_put.py` - 6 endpoint tests

**Files Modified**:

- `backend/app/schemas/job_posting.py` - Added JobPostingUpdate schema
- `backend/app/services/job_posting_service.py` - Added update_job_posting()
- `backend/app/api/v1/endpoints/job_postings.py` - Added PUT /{id} endpoint

**Tests**: 6/6 passing

- test_update_job_posting_success
- test_update_job_posting_timestamp_changes
- test_update_job_posting_not_found_returns_404
- test_update_job_posting_other_user_returns_404
- test_update_job_posting_empty_title_returns_422
- test_update_job_posting_unauthenticated_returns_401

**Key Features**:

- Updates all fields and explicit updated_at timestamp
- Enforces ownership check before update
- Validates data with Pydantic
  - [ ] Test partial update (all fields vs. selective fields)

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- Authorization: User can only update THEIR OWN job postings
- RESTful pattern: PUT /api/v1/job-postings/{id} (full replacement)
- Automatic timestamp update: updated_at should reflect modification time
- 404 for ownership violations: Treat same as "not found" (don't leak existence)
- Full replacement: All fields must be provided (PUT semantics)

### Technical Implementation Details

**Suggested files:**

- `backend/app/schemas/job_posting.py` - Add JobPostingUpdate schema
- `backend/app/services/job_posting_service.py` - Add update function
- `backend/app/api/v1/endpoints/job_postings.py` - Add PUT endpoint
- `backend/tests/api/v1/test_job_postings_put.py` - Endpoint tests

**Pydantic Schema:**

```python
class JobPostingUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description: str = Field(..., min_length=1, max_length=10000)
    experience_level: Optional[str] = Field(None, max_length=50)
    tech_stack: Optional[List[str]] = None
```

**Service Layer:**

```python
async def update_job_posting(
    db: AsyncSession,
    job_posting_id: UUID,
    user_id: UUID,
    data: JobPostingUpdate
) -> JobPosting:
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

    job_posting.title = data.title
    job_posting.company = data.company
    job_posting.description = data.description
    job_posting.experience_level = data.experience_level
    job_posting.tech_stack = data.tech_stack
    job_posting.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(job_posting)
    return job_posting
```

**API Endpoint:**

```python
@router.put("/{job_posting_id}", response_model=JobPostingResponse)
async def update_job_posting(
    job_posting_id: UUID,
    job_posting_data: JobPostingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job_posting = await job_posting_service.update_job_posting(
        db, job_posting_id, current_user.id, job_posting_data
    )
    return job_posting
```

**Error Handling:**

- 404 Not Found: Job posting doesn't exist OR user doesn't own it
- 422 Validation Error: Missing required fields or validation failures
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create job posting, then update it, verify all fields and updated_at changed
- Attempt update of non-existent job posting (404)
- Create job posting for user A, authenticate as user B, attempt update (404)
- Update with invalid data (empty title, description too long)
- Verify id, user_id, created_at remain unchanged
- Test authentication requirements

### Dependencies

- Requires JobPosting model from story 3.6
- Requires job posting service from stories 3.7-3.9
- Requires authentication from Epic 2

### Timestamp Behavior

- **created_at:** NEVER changes (records original creation time)
- **updated_at:** ALWAYS updated on modification
- Both timestamps use UTC timezone

### REST Semantics

- **PUT = Full replacement** (all fields must be provided)
- **Future PATCH:** If partial updates needed, implement PATCH endpoint
- Current implementation: Full replacement only (PUT)

### Authorization Pattern

- Query filters by BOTH id AND user_id
- Returns 404 for ownership violations (security best practice)
- Don't reveal existence of other users' job postings

### User Experience Considerations

- Frontend should show "last updated" timestamp
- Consider "unsaved changes" indicator before PUT request
- Pre-populate form with current values for editing
- Optimistic UI update recommended

### Data Integrity Considerations

- If interview sessions reference this job posting, updates don't affect past
  sessions
- Job posting data may be snapshot at session creation (Epic 4 design decision)
- Update doesn't invalidate existing interview sessions

### Performance Considerations

- Single record update - no performance concerns
- Composite query (id + user_id) uses primary key index
- Updated_at timestamp handled explicitly in service layer

### Security Considerations

- User isolation enforced via composite query (id AND user_id)
- 404 for ownership violations prevents information disclosure
- Field validation prevents malicious large payloads
- No additional authorization needed beyond authentication

### Future Considerations

- If interview sessions store snapshot of job posting, consider showing "This
  job posting has been updated since this session was created"
- Consider audit trail for job posting updates (who changed what when)
- May need versioning if job posting history becomes important
