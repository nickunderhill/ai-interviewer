# Story 5.2: Implement Feedback Analysis Service

Status: ready-for-dev

## Story

As a developer, I want to create a service to analyze answers using OpenAI, so
that we generate comprehensive multi-dimensional feedback.

## Acceptance Criteria

1. **Given** I'm implementing feedback generation **When** the service receives
   a completed session **Then** it fetches all Q&A pairs (SessionMessages) for
   the session **And** constructs a prompt asking OpenAI to analyze across 4
   dimensions: technical accuracy, communication clarity, problem-solving
   approach, relevance to job requirements **And** the prompt includes the job
   posting context and résumé **And** requests structured JSON output with
   scores (0-100) and text feedback for each dimension **And** requests
   identification of knowledge gaps and learning recommendations **And** calls
   OpenAI API (via OpenAI service) to generate feedback **And** parses the
   response into structured feedback data **And** handles errors if OpenAI call
   fails

## Tasks / Subtasks

- [ ] Task 1: Define structured response contract (AC: #1)

  - [ ] Create `backend/app/schemas/feedback_analysis.py` (or colocate in
        `schemas/feedback.py`) with a Pydantic model representing OpenAI JSON
        output
  - [ ] Include fields:
    - [ ] dimension scores (0..100)
    - [ ] dimension feedback text
    - [ ] knowledge_gaps: list[str]
    - [ ] learning_recommendations: list[str]
    - [ ] optional: overall_comments
  - [ ] Add validators to clamp/validate scores range

- [ ] Task 2: Implement feedback analysis service (AC: #1)

  - [ ] Create `backend/app/services/feedback_analysis_service.py`
  - [ ] Add function:
        `analyze_session(db: AsyncSession, session_id: UUID, current_user: User) -> FeedbackAnalysisResult`
  - [ ] Load session with relationships:
    - [ ] `InterviewSession.job_posting`
    - [ ] `InterviewSession.user.resume`
    - [ ] `InterviewSession.messages` ordered ASC
  - [ ] Extract Q&A pairs from `SessionMessage` list
  - [ ] Build prompt that includes:
    - [ ] job posting: title + description + tech_stack
    - [ ] resume content (plain text)
    - [ ] Q&A transcript
    - [ ] explicit JSON schema with keys and score ranges
  - [ ] Call OpenAI via existing `OpenAIService`
        (`backend/app/services/openai_service.py`) instantiated per-user
  - [ ] Parse response:
    - [ ] `json.loads()`
    - [ ] validate with Pydantic model
  - [ ] Error handling:
    - [ ] if parsing fails → raise HTTPException with code like
          `FEEDBACK_PARSE_FAILED`
    - [ ] if OpenAI call fails → surface sanitized error (do not leak prompt or
          API key)

- [ ] Task 3: Unit tests for service (AC: #1)

  - [ ] Create `backend/tests/services/test_feedback_analysis_service.py`
  - [ ] Mock OpenAIService to return deterministic JSON
  - [ ] Test:
    - [ ] happy path parsing and validation
    - [ ] missing resume/job posting error paths
    - [ ] malformed JSON response handled
    - [ ] score out-of-range clamped or rejected (pick one behavior and enforce)

## Dev Notes

### Critical Architecture Requirements

- **BYOK security:** never log the user API key or decrypted key.
- **Use existing OpenAI integration:** route all calls through `OpenAIService`.
- **Do not block HTTP request** in this story: this is service-only; async
  orchestration is story 5.3.
- **Prompting discipline:** request strict JSON; include an explicit schema;
  instruct model to output JSON only.

### Prompt Contract (recommendation)

Request JSON with this shape (example keys):

```json
{
  "technical_accuracy_score": 0,
  "communication_clarity_score": 0,
  "problem_solving_score": 0,
  "relevance_score": 0,
  "technical_feedback": "...",
  "communication_feedback": "...",
  "problem_solving_feedback": "...",
  "relevance_feedback": "...",
  "overall_comments": "...",
  "knowledge_gaps": ["..."],
  "learning_recommendations": ["..."]
}
```

### Technical Implementation Details

**Suggested files:**

```
backend/app/services/feedback_analysis_service.py   # NEW
backend/app/schemas/feedback.py                    # UPDATE or NEW schema file
backend/tests/services/test_feedback_analysis_service.py  # NEW
```

**Implementation sketch:**

```python
import json
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview_session import InterviewSession
from app.models.user import User
from app.services.openai_service import OpenAIService
from app.schemas.feedback import FeedbackAnalysisResult

async def analyze_session(db: AsyncSession, session_id: UUID, current_user: User) -> FeedbackAnalysisResult:
    session = await db.get(InterviewSession, session_id)
    # Prefer loading with select + selectinload to ensure relationships are present

    openai = OpenAIService(current_user)

    prompt = build_prompt(session)
    raw = openai.generate_chat_completion(messages=[{"role": "user", "content": prompt}])

    try:
        data = json.loads(raw)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "FEEDBACK_PARSE_FAILED", "message": "AI feedback response could not be parsed"},
        )

    return FeedbackAnalysisResult.model_validate(data)
```

### References

- [OpenAI service patterns: backend/app/services/openai_service.py]
- [Operation async pattern:
  _bmad-output/implementation-artifacts/4-8-create-question-generation-endpoint-with-async-pattern.md]
- [Project Context: _bmad-output/project-context.md#Long-Running Operations]

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

- Deterministic schema validated output
- Robust error handling and sanitization

### File List

_To be filled by dev agent_
