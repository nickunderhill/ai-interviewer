# Story 3.8: Create Job Posting List Endpoint

Status: done

## Story

As a user, I want to view all my saved job postings, so that I can see which
positions I can practice for.

## Acceptance Criteria

1. **Given** I am authenticated and have created job postings **When** I GET
   `/api/v1/job-postings` **Then** the system returns a list of all my job
   postings **And** each posting includes id, title, company, experience_level,
   tech_stack, created_at **And** only my job postings are returned (filtered by
   user_id) **And** if I have no job postings, it returns an empty array **And**
   the list is ordered by created_at descending (newest first)

## Tasks / Subtasks

- [x] Task 1: Create list response schema (AC: #1)

  - [x] Add JobPostingListItem schema to `backend/app/schemas/job_posting.py`
  - [x] Include fields: id, title, company, experience_level, tech_stack,
        created_at
  - [x] Exclude description (too large for list view)

- [x] Task 2: Implement job posting list service (AC: #1)

  - [x] Add function to `backend/app/services/job_posting_service.py`
  - [x] Function:
        `get_user_job_postings(db: AsyncSession, user_id: UUID) -> List[JobPosting]`
  - [x] Query all job postings for user_id
  - [x] Order by created_at descending (newest first)
  - [x] Return list of JobPosting objects (empty list if none)

- [x] Task 3: Implement GET /api/v1/job-postings endpoint (AC: #1)

  - [x] Add GET endpoint to `backend/app/api/v1/endpoints/job_postings.py`
  - [x] Endpoint protected with `get_current_user` dependency
  - [x] Call job posting service to retrieve list
  - [x] Return 200 OK with array of job postings
  - [x] Return empty array if user has no job postings

- [x] Task 4: Add endpoint tests (AC: #1)
  - [x] Test returns list of user's job postings
  - [x] Test returns empty array when user has no job postings
  - [x] Test ordering (newest first)
  - [x] Test user isolation (user A cannot see user B's job postings)
  - [x] Test 401 for unauthenticated request

---

## Implementation Summary

**Status**: Completed on 2025-12-22

**Files Created**:

- `backend/tests/api/v1/test_job_postings_list.py` - 5 endpoint tests

**Files Modified**:

- `backend/app/schemas/job_posting.py` - Added JobPostingListItem (excludes
  description)
- `backend/app/services/job_posting_service.py` - Added get_user_job_postings()
- `backend/app/api/v1/endpoints/job_postings.py` - Added GET / endpoint

**Tests**: 5/5 passing

- test_list_job_postings_success
- test_list_job_postings_empty_returns_empty_array
- test_list_job_postings_ordered_by_created_at_desc
- test_list_job_postings_user_isolation
- test_list_job_postings_unauthenticated_returns_401

**Key Features**:

- Returns array without description field for performance
- Orders by created_at DESC (newest first)
- Enforces user isolation

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency
- User isolation: User can only retrieve THEIR OWN job postings (via user_id
  from token)
- RESTful pattern: GET /api/v1/job-postings (collection endpoint)
- Ordering: created_at DESC (newest first)
- Empty array: When user has no job postings (not 404, just empty list)
- List optimization: Exclude description field (reduce payload size)

### Technical Implementation Details

**Suggested files:**

- `backend/app/schemas/job_posting.py` - Add JobPostingListItem schema
- `backend/app/services/job_posting_service.py` - Add list function
- `backend/app/api/v1/endpoints/job_postings.py` - Add GET endpoint
- `backend/tests/api/v1/test_job_postings_list.py` - Endpoint tests

**Pydantic Schema:**

```python
class JobPostingListItem(BaseModel):
    id: UUID
    title: str
    company: Optional[str]
    experience_level: Optional[str]
    tech_stack: Optional[List[str]]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Service Layer:**

```python
async def get_user_job_postings(
    db: AsyncSession,
    user_id: UUID
) -> List[JobPosting]:
    result = await db.execute(
        select(JobPosting)
        .where(JobPosting.user_id == user_id)
        .order_by(JobPosting.created_at.desc())
    )
    return result.scalars().all()
```

**API Endpoint:**

```python
@router.get("/", response_model=List[JobPostingListItem])
async def list_job_postings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job_postings = await job_posting_service.get_user_job_postings(
        db, current_user.id
    )
    return job_postings
```

**Response Format:**

- Returns array of JobPostingListItem objects
- Empty array `[]` when user has no job postings
- Excludes description field (use detail endpoint for full data)
- Ordered by created_at DESC

**Error Handling:**

- 200 OK: Always returned (even with empty array)
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Create multiple job postings, verify all returned
- Verify ordering (newest first)
- Create job postings for user A, authenticate as user B, verify empty array
- Test with no job postings (empty array)
- Test authentication requirements

### Dependencies

- Requires JobPosting model from story 3.6
- Requires job posting service from story 3.7
- Requires authentication from Epic 2

### Performance Considerations

- Query indexed on user_id (foreign key automatically indexed)
- Description field excluded to reduce payload size
- No pagination in MVP (acceptable for reasonable number of job postings)
- Future: Add pagination if users have 100+ job postings

### List vs Detail Pattern

- **List endpoint:** Summary data without description (lightweight)
- **Detail endpoint:** Full data including description (story 3.9)
- Frontend: List view for selection, detail view for full information

### Ordering Rationale

- created_at DESC = Newest first
- Assumption: Users are more interested in recently added job postings
- Alternative: Could order by title alphabetically (not implemented in MVP)

### User Experience Considerations

- Frontend should show clear "No job postings yet" message for empty array
- List view should be scannable (title, company, experience level)
- Consider showing job posting count in UI header
- Enable quick navigation from list to detail view

### Security Considerations

- User isolation enforced via authentication and user_id filtering
- No additional authorization needed (user can always access their own job
  postings)
- Job posting data is user's own content - no privacy concerns

### Future Enhancements

- Pagination (if needed for large datasets)
- Filtering by experience_level or tech_stack
- Search by title or company name
- Sorting options (by title, company, date)
