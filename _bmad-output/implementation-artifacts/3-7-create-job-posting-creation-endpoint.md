# Story 3.7: Create Job Posting Creation Endpoint

Status: done

## Story

As a user, I want to create a new job posting with description, role title,
experience level, and tech stack, so that I can practice interviews for specific
positions.

## Acceptance Criteria

1. **Given** I am authenticated **When** I POST to `/api/v1/job-postings` with
   job posting data **Then** the system validates all required fields (title,
   description) are present **And** a JobPosting record is created associated
   with my user_id **And** the endpoint returns 201 Created with the job posting
   data **And** experience_level and tech_stack are optional fields **And**
   unauthenticated requests return 401 Unauthorized

## Tasks / Subtasks

- [x] Task 1: Create Pydantic schemas for job posting (AC: #1)

  - [x] Create `backend/app/schemas/job_posting.py`
  - [x] JobPostingCreate schema: title (required), company (optional),
        description (required), experience_level (optional), tech_stack
        (optional List[str])
  - [x] JobPostingResponse schema: id, user_id, title, company, description,
        experience_level, tech_stack, created_at, updated_at
  - [x] Add validation for required fields and reasonable max lengths

- [x] Task 2: Implement job posting creation service (AC: #1)

  - [x] Create `backend/app/services/job_posting_service.py`
  - [x] Function:
        `create_job_posting(db: AsyncSession, user_id: UUID, data: JobPostingCreate) -> JobPosting`
  - [x] Create JobPosting record with user_id and provided data
  - [x] Return created JobPosting object

- [x] Task 3: Implement POST /api/v1/job-postings endpoint (AC: #1)

  - [x] Create `backend/app/api/v1/endpoints/job_postings.py`
  - [x] POST endpoint protected with `get_current_user` dependency
  - [x] Call job posting service to create job posting
  - [x] Return 201 Created with job posting data
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 4: Add endpoint tests (AC: #1)

  - [x] Test successful creation returns 201
  - [x] Test with all fields populated
  - [x] Test with only required fields (title, description)
  - [x] Test missing required fields returns 422 Validation Error
  - [x] Test unauthenticated request returns 401
  - [x] Test tech_stack array storage

- [x] Task 5: Register job posting router in main app
  - [x] Import job posting router in `backend/app/main.py`
  - [x] Register with prefix `/api/v1/job-postings`

---

## Implementation Summary

**Status**: Completed on 2025-12-22

**Files Created**:

- `backend/app/schemas/job_posting.py` - Pydantic schemas (JobPostingCreate,
  JobPostingResponse, JobPostingUpdate, JobPostingListItem)
- `backend/app/services/job_posting_service.py` - Complete service with all CRUD
  operations
- `backend/app/api/v1/endpoints/job_postings.py` - POST endpoint (and other CRUD
  endpoints)
- `backend/tests/api/v1/test_job_postings_post.py` - 9 endpoint tests

**Files Modified**:

- `backend/app/main.py` - Registered job_postings_router

**Tests**: 9/9 passing for POST endpoint

- test_create_job_posting_success
- test_create_job_posting_only_required_fields
- test_create_job_posting_missing_title_returns_422
- test_create_job_posting_empty_title_returns_422
- test_create_job_posting_title_too_long_returns_422
- test_create_job_posting_description_too_long_returns_422
- test_create_job_posting_unauthenticated_returns_401
- test_create_job_posting_with_tech_stack
- test_create_multiple_job_postings

**Coverage**: 100% for schemas, 78% for endpoints

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency from Epic 2
- One-to-many relationship: User can create unlimited job postings
- Required fields: title, description
- Optional fields: company, experience_level, tech_stack
- RESTful API pattern: POST /api/v1/job-postings for creation
- Tech stack stored as array (JSONB in database, List[str] in Pydantic)

### Technical Implementation Details

**Suggested files:**

- `backend/app/schemas/job_posting.py` - Pydantic schemas
- `backend/app/services/job_posting_service.py` - Business logic
- `backend/app/api/v1/endpoints/job_postings.py` - API endpoint
- `backend/tests/api/v1/test_job_postings_post.py` - Endpoint tests
- `backend/tests/services/test_job_posting_service.py` - Service tests

**Pydantic Schemas:**

```python
class JobPostingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    description: str = Field(..., min_length=1, max_length=10000)
    experience_level: Optional[str] = Field(None, max_length=50)
    tech_stack: Optional[List[str]] = None

class JobPostingResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    company: Optional[str]
    description: str
    experience_level: Optional[str]
    tech_stack: Optional[List[str]]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Service Layer:**

```python
async def create_job_posting(
    db: AsyncSession,
    user_id: UUID,
    data: JobPostingCreate
) -> JobPosting:
    job_posting = JobPosting(
        user_id=user_id,
        title=data.title,
        company=data.company,
        description=data.description,
        experience_level=data.experience_level,
        tech_stack=data.tech_stack
    )
    db.add(job_posting)
    await db.commit()
    await db.refresh(job_posting)
    return job_posting
```

**API Endpoint:**

```python
@router.post("/", status_code=201, response_model=JobPostingResponse)
async def create_job_posting(
    job_posting_data: JobPostingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    job_posting = await job_posting_service.create_job_posting(
        db, current_user.id, job_posting_data
    )
    return job_posting
```

**Error Handling:**

- 422 Validation Error: Missing required fields (title, description) or
  validation failures
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors

**Testing Strategy:**

- Happy path: Create job posting with all fields
- Minimal path: Create with only required fields (title, description)
- Validation: Missing title, missing description, empty strings
- Auth: No token, invalid token
- Tech stack: Empty array, single item, multiple items, null
- Edge cases: Very long description, special characters in title

### Dependencies

- Requires JobPosting model from story 3.6
- Requires User model and authentication from Epic 2
- Requires `get_current_user` dependency from story 2.6

### Validation Rules

- **title:** Required, 1-255 characters
- **company:** Optional, max 255 characters
- **description:** Required, 1-10,000 characters
- **experience_level:** Optional, max 50 characters (e.g., "Junior",
  "Mid-level", "Senior")
- **tech_stack:** Optional, array of strings (e.g., ["Python", "React",
  "PostgreSQL"])

### User Experience Considerations

- Frontend form should have clear required field indicators
- Tech stack input: Consider autocomplete or multi-select component
- Experience level: Consider dropdown with predefined options
- Description: Textarea with character counter

### Data Integrity

- No duplicate checking required (user can save multiple postings for same
  company/role)
- All fields properly sanitized by Pydantic validation
- Tech stack stored as array for future query capabilities

### Integration Points

- Job postings will be used as dual-context for AI question generation in Epic 4
- Job posting must exist before creating interview session (Epic 4 story 4.2)
- Job posting referenced by InterviewSession model (foreign key relationship)

### Security Considerations

- Job postings are user's own data - access control via authentication
- No HTML sanitization needed (stored as plain text, rendered safely by React)
- Rate limiting recommended (prevent abuse with bulk creation)
- Field length validation prevents DoS via large payloads
