# Story 8.15: Implement Input Validation and Sanitization

Status: done

## Story

As a developer, I want to validate and sanitize all user inputs, so that the
system is protected against injection attacks.

## Acceptance Criteria

1. **Given** all API endpoints accept user input **When** a request is received
   **Then** Pydantic models validate all input fields (types, required fields,
   formats) **And** string inputs are validated for max length to prevent DoS
   **And** SQL injection is prevented by using SQLAlchemy ORM (no raw SQL with
   user input) **And** XSS is prevented by proper output encoding in the
   frontend **And** email format is validated with regex **And** error messages
   for validation failures are clear and don't expose system internals **And**
   follows OWASP input validation guidelines (NFR5, NFR10) ✅

## Tasks / Subtasks

- [x] Task 1: Audit all request schemas for validation gaps (AC: #1)

  - [x] Add max_length constraints for text fields (resume, job description,
        answers)
  - [x] Validate enums for status/type fields

- [x] Task 2: Add centralized validators (AC: #1)

  - [x] Email validation (via `EmailStr`)
  - [x] String length guards (schema-level `max_length`)
  - [x] Optional sanitization for freeform text (trim + NUL byte rejection)

- [x] Task 3: Ensure ORM-only queries (AC: #1)

  - [x] Search for any raw SQL usages
  - [x] Confirm no raw SQL with user input

- [x] Task 4: Improve validation error responses (AC: #1)

  - [x] Ensure FastAPI returns structured error format
  - [x] Avoid leaking stack traces or internals

- [x] Task 5: Frontend input constraints (AC: #1)

  - [x] Zod schemas mirror backend constraints where forms exist
  - [x] Show clear, friendly field errors

- [x] Task 6: Tests (AC: #1)
  - [x] Oversized payload rejected
  - [x] Invalid email rejected
  - [x] Invalid enum rejected

## Dev Notes

### Critical Architecture Requirements

- Pydantic v2 schemas in `backend/app/schemas/`
- React Hook Form + Zod in frontend
- Avoid raw SQL

### File Structure

```
backend/app/
├── schemas/
│   └── *.py
├── utils/
│   └── validators.py
└── tests/
    └── test_validation.py

frontend/src/
└── features/
    └── */
        └── validation.ts
```

### Implementation Details

**Pydantic v2 constraints example:**

```python
# backend/app/schemas/job_posting.py
from pydantic import BaseModel, Field

class JobPostingCreate(BaseModel):
    role_title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=20000)
    experience_level: str = Field(min_length=1, max_length=40)
    tech_stack: str = Field(min_length=0, max_length=500)
```

**Email validation example:**

```python
# backend/app/schemas/auth.py
from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
```

**Frontend Zod example:**

```ts
import { z } from 'zod';

export const jobPostingSchema = z.object({
  role_title: z.string().min(1).max(120),
  description: z.string().min(1).max(20000),
  experience_level: z.string().min(1).max(40),
  tech_stack: z.string().max(500).optional(),
});
```

### Testing Requirements

- Invalid inputs return 422 with clear messages
- No internal stack traces

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.15]
- [Source: _bmad-output/project-context.md#Input-Validation]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Added centralized text normalization helpers (`normalize_text`,
  `ensure_not_blank`)
- Hardened request schemas with `max_length` and trimming for freeform text
- Added enum-like validation for session `status` filter via `Literal[...]`
- Frontend: enforced `max(128)` password rules in Zod; answer textarea capped at
  20,000 chars
- Added backend tests for invalid email, oversized password, and invalid status
  enum

### Code Review

**Review Date:** 2025-12-27 \
**Reviewer:** GitHub Copilot (GPT-5.2) \
**Result:** ✅ Approved

**Acceptance Criteria Verification (AC #1):**

- ✅ Pydantic models validate types/formats and enforce max-length caps (notably
  password max 128, answer max 20,000, API key max 256).
- ✅ SQL injection risk minimized: request handling uses SQLAlchemy ORM; only
  benign `text("SELECT 1")` health-check style queries found.
- ✅ XSS mitigation: no `dangerouslySetInnerHTML` usage found in `frontend/src`;
  React rendering provides output encoding by default.
- ✅ Email validation: uses `EmailStr` (library-based validation) rather than a
  handwritten regex; functionally meets the “valid email” requirement with
  stronger semantics.
- ✅ Validation failures return structured FastAPI errors (422) without stack
  traces.

**Notes / Minor Gaps:**

- The “File Structure” section references `frontend/src/**/validation.ts` as a
  target pattern; this repo currently applies Zod constraints directly in the
  existing form components (auth + answer form). If additional forms (job
  posting/resume) are added later, consider centralizing shared Zod schemas to
  match the doc snippet.

**Test Evidence:**

- Backend: `pytest -q tests/test_validation.py` (3 passed)
