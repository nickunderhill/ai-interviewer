# Story 5.5: Create Feedback Retrieval Endpoint

Status: ready-for-dev

## Story

As a user, I want to view AI-generated feedback for a completed interview, so
that I can understand my performance across all dimensions.

## Acceptance Criteria

1. **Given** I am authenticated and have a completed session with feedback
   **When** I GET `/api/v1/sessions/{id}/feedback` **Then** the system validates
   I own the session **And** returns the InterviewFeedback record with all
   dimension scores, feedback text, overall_score, knowledge_gaps, and
   learning_recommendations **And** returns 200 OK **And** if feedback doesn't
   exist yet, returns 404 Not Found **And** if the session doesn't exist or
   belongs to another user, returns 404 Not Found

## Tasks / Subtasks

- [ ] Task 1: Add response schema (AC: #1)

  - [ ] Ensure `backend/app/schemas/feedback.py` has `InterviewFeedbackResponse`
  - [ ] Ensure JSON arrays serialize as lists

- [ ] Task 2: Implement GET endpoint (AC: #1)

  - [ ] Update `backend/app/api/v1/endpoints/sessions.py`
  - [ ] Add `GET /api/v1/sessions/{session_id}/feedback`
  - [ ] Validate session belongs to current user (404 if not)
  - [ ] Lookup feedback by session_id
  - [ ] Return 404 if no feedback
  - [ ] Return 200 with feedback response

- [ ] Task 3: Add endpoint tests (AC: #1)

  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py` (or dedicated file)
  - [ ] Test:
    - [ ] 200 returns feedback for owned session
    - [ ] 404 when feedback missing
    - [ ] 404 for session not found / not owned
    - [ ] 401 when unauthenticated

## Dev Notes

### Critical Architecture Requirements

- **Authorization:** treat unauthorized and non-existent as 404 to avoid leaking
  existence.
- **Response shape:** include all dimension scores + feedback text +
  overall_score + gaps + recommendations.
- **No sensitive data:** do not return resume content or job posting unless
  explicitly required by endpoint.

### Technical Implementation Details

**Suggested files:**

```
backend/app/api/v1/endpoints/sessions.py   # UPDATE
backend/app/schemas/feedback.py            # NEW/UPDATE
backend/tests/api/v1/test_sessions.py      # UPDATE
```

**Endpoint sketch:**

```python
@router.get(
    "/{session_id}/feedback",
    response_model=InterviewFeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI feedback for a session",
)
async def get_feedback(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify session ownership
    await session_service.get_session_by_id(db, session_id, current_user)

    feedback = await feedback_service.get_feedback_by_session_id(db, session_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "FEEDBACK_NOT_FOUND", "message": "Feedback not found for this session"},
        )

    return InterviewFeedbackResponse.model_validate(feedback)
```

### References

- Session endpoint conventions: `backend/app/api/v1/endpoints/sessions.py`
- Error format standard: `_bmad-output/project-context.md#API Patterns`

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

- 404 returned for missing feedback or unauthorized session
- Response includes all scores and arrays

### File List

_To be filled by dev agent_
