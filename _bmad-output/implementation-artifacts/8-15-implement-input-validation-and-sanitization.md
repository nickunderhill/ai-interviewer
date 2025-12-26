# Story 8.15: Implement Input Validation and Sanitization

Status: ready-for-dev

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

- [ ] Task 1: Audit all request schemas for validation gaps (AC: #1)

  - [ ] Add max_length constraints for text fields (resume, job description)
  - [ ] Validate enums for status/type fields

- [ ] Task 2: Add centralized validators (AC: #1)

  - [ ] Email regex validation
  - [ ] String length guards
  - [ ] Optional HTML stripping for freeform text (if needed)

- [ ] Task 3: Ensure ORM-only queries (AC: #1)

  - [ ] Search for any raw SQL usages
  - [ ] Replace with SQLAlchemy constructs

- [ ] Task 4: Improve validation error responses (AC: #1)

  - [ ] Ensure FastAPI returns structured error format
  - [ ] Avoid leaking stack traces or internals

- [ ] Task 5: Frontend input constraints (AC: #1)

  - [ ] Zod schemas mirror backend constraints
  - [ ] Show clear, friendly field errors

- [ ] Task 6: Tests (AC: #1)
  - [ ] Oversized payload rejected
  - [ ] Invalid email rejected
  - [ ] Invalid enum rejected

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

- Adds schema-level constraints + aligned frontend validation
- Includes DoS-size guards and testing checklist
