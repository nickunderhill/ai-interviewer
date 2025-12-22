# Story 3.2: Create Resume Upload/Paste Endpoint

Status: done

## Story

As a user, I want to upload or paste my résumé content in text format, so that I
can use it as context for AI-generated interview questions.

## Acceptance Criteria

1. **Given** I am authenticated **When** I POST to `/api/v1/resumes` with résumé
   content (text) **Then** the system validates the content is not empty **And**
   a Resume record is created associated with my user_id **And** the endpoint
   returns 201 Created with the résumé data **And** if I already have a résumé,
   it returns 409 Conflict (one résumé per user) **And** unauthenticated
   requests return 401 Unauthorized

## Tasks / Subtasks

- [x] Task 1: Create Pydantic schemas for resume (AC: #1)

  - [x] Create `backend/app/schemas/resume.py`
  - [x] ResumeCreate schema: content (str, min_length=1, max_length=50000)
  - [x] ResumeResponse schema: id, user_id, content, created_at, updated_at
  - [x] Add validation for content field (not empty, reasonable max length)

- [x] Task 2: Implement resume creation service (AC: #1)

  - [x] Create `backend/app/services/resume_service.py`
  - [x] Function:
        `create_resume(db: AsyncSession, user_id: UUID, content: str) -> Resume`
  - [x] Check if user already has a resume (raise ConflictException if exists)
  - [x] Create Resume record with user_id and content
  - [x] Return created Resume object

- [x] Task 3: Implement POST /api/v1/resumes endpoint (AC: #1)

  - [x] Create `backend/app/api/v1/endpoints/resumes.py`
  - [x] POST endpoint protected with `get_current_user` dependency
  - [x] Call resume service to create resume
  - [x] Return 201 Created with resume data
  - [x] Return 409 Conflict if user already has resume
  - [x] Return 401 Unauthorized for unauthenticated requests

- [x] Task 4: Add endpoint tests (AC: #1)

  - [x] Test successful resume creation returns 201
  - [x] Test duplicate resume returns 409 Conflict
  - [x] Test empty content returns 422 Validation Error
  - [x] Test unauthenticated request returns 401
  - [x] Test content validation (min/max length)

- [x] Task 5: Register resume router in main app
  - [x] Import resume router in `backend/app/main.py`
  - [x] Register with prefix `/api/v1/resumes`

## Dev Notes

### Critical Architecture Requirements

- Authentication required: Use `get_current_user` dependency from Epic 2
- One-to-one relationship: Each user can have only ONE resume
- Content validation: Not empty, reasonable max length (~50KB)
- RESTful API pattern: POST /api/v1/resumes for creation
- Response excludes sensitive user data, returns resume data only

### Technical Implementation Details

**Suggested files:**

- `backend/app/schemas/resume.py` - Pydantic schemas
- `backend/app/services/resume_service.py` - Business logic
- `backend/app/api/v1/endpoints/resumes.py` - API endpoint
- `backend/tests/api/v1/test_resumes_post.py` - Endpoint tests
- `backend/tests/services/test_resume_service.py` - Service tests

**Pydantic Schemas:**

```python
class ResumeCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=50000)

class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

**Service Layer:**

```python
async def create_resume(
    db: AsyncSession,
    user_id: UUID,
    content: str
) -> Resume:
    # Check if user already has resume
    existing = await db.execute(
        select(Resume).where(Resume.user_id == user_id)
    )
    if existing.scalar_one_or_none():
        raise ConflictException("User already has a resume")

    # Create new resume
    resume = Resume(user_id=user_id, content=content)
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume
```

**API Endpoint:**

```python
@router.post("/", status_code=201, response_model=ResumeResponse)
async def create_resume(
    resume_data: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    resume = await resume_service.create_resume(
        db, current_user.id, resume_data.content
    )
    return resume
```

**Error Handling:**

- 409 Conflict: User already has a resume (business rule)
- 422 Validation Error: Empty content or exceeds max length
- 401 Unauthorized: Missing or invalid authentication token
- 500 Internal Server Error: Database errors (with proper logging)

**Testing Strategy:**

- Happy path: Create resume with valid content
- Conflict path: Attempt to create second resume for same user
- Validation path: Empty content, content too long
- Auth path: No token, invalid token, expired token
- Edge cases: Unicode content, special characters, whitespace-only content

### Dependencies

- Requires Resume model from story 3.1
- Requires User model and authentication from Epic 2
- Requires `get_current_user` dependency from story 2.6

### Integration Points

- Resume content will be used as dual-context for AI question generation in Epic
  4
- Resume must be created before starting interview sessions (Epic 4 story 4.2)

### Validation Rules

- **Content min length:** 1 character (not empty)
- **Content max length:** 50,000 characters (~10-15 pages of text)
- **Content format:** Plain text (no special formatting required)
- **Whitespace:** Trimmed but allowed within content

### Security Considerations

- Resume content is user's own PII - access control via authentication
- No HTML sanitization needed (stored as plain text, rendered safely by React)
- Rate limiting recommended (prevent abuse with large uploads)
- Content length validation prevents DoS via large payloads

## Dev Agent Record

### Implementation Notes

✅ **All tasks completed** - Story 3.2 implemented following TDD

**Created Files:**

- `backend/app/schemas/resume.py` - Pydantic schemas (ResumeCreate,
  ResumeResponse)
- `backend/app/services/resume_service.py` - Business logic with
  ResumeConflictException
- `backend/app/api/v1/endpoints/resumes.py` - POST /api/v1/resumes endpoint
- `backend/tests/api/v1/test_resumes_post.py` - 7 endpoint tests
- `backend/tests/services/test_resume_service.py` - 4 service tests

**Modified Files:**

- `backend/app/main.py` - Registered resumes router

**Test Results:**

- 11/11 tests passing (100%)
- Coverage: resume_service.py 100%, resumes.py 92%

**Key Decisions:**

- Used HTTP 409 Conflict for duplicate resume (one-to-one relationship
  enforcement)
- 50KB max length strikes balance between usability and DoS prevention
- Pydantic validation handles min_length/max_length automatically
- Service layer raises custom ResumeConflictException for business rule
  violation

## File List

**Created:**

- backend/app/schemas/resume.py
- backend/app/services/resume_service.py
- backend/app/api/v1/endpoints/resumes.py
- backend/tests/api/v1/test_resumes_post.py
- backend/tests/services/test_resume_service.py

**Modified:**

- backend/app/main.py

## Change Log

- 2025-12-22 14:30: Code review fixes - added whitespace validation test,
  improved module docstring, added rate limiting TODO
- 2025-12-22: Implemented POST /api/v1/resumes endpoint with comprehensive tests
