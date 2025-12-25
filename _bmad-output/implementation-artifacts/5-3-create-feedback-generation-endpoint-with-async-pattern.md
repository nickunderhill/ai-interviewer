# Story 5.3: Create Feedback Generation Endpoint with Async Pattern

Status: ready-for-dev

## Story

As a user, I want to request AI feedback for a completed interview, so that I
can understand my performance.

## Acceptance Criteria

1. **Given** I am authenticated with a completed session **When** I POST to
   `/api/v1/sessions/{id}/generate-feedback` **Then** the system validates I own
   the session and it's completed **And** validates feedback doesn't already
   exist for this session **And** creates an Operation record with
   status='pending' and type='feedback_analysis' **And** returns 202 Accepted
   with operation_id immediately **And** starts a background task to generate
   feedback (using analysis service) **And** updates the Operation status to
   'processing' then 'completed' with result, or 'failed' with error_message
   **And** if the session is not completed, returns 400 Bad Request **And** if
   feedback already exists, returns 409 Conflict

## Tasks / Subtasks

- [ ] Task 1: Add background task for feedback generation (AC: #1)

  - [ ] Create `backend/app/tasks/feedback_tasks.py`
  - [ ] Implement async task:
        `generate_feedback_task(operation_id: UUID, session_id: UUID, user_id: UUID)`
  - [ ] Load Operation and set status='processing'
  - [ ] Load session and validate ownership (defense-in-depth)
  - [ ] Call feedback analysis service (story 5.2)
  - [ ] On success:
    - [ ] store JSON result on Operation.result
    - [ ] set status='completed'
  - [ ] On failure:
    - [ ] set status='failed'
    - [ ] set sanitized error_message

- [ ] Task 2: Add endpoint to sessions router (AC: #1)

  - [ ] Update `backend/app/api/v1/endpoints/sessions.py`
  - [ ] Add `POST /api/v1/sessions/{session_id}/generate-feedback`
  - [ ] Validate:
    - [ ] session exists and belongs to current user
    - [ ] session.status == 'completed' else 400
    - [ ] feedback does not already exist else 409
  - [ ] Create Operation record:
    - [ ] `operation_type='feedback_analysis'`
    - [ ] `status='pending'`
  - [ ] Enqueue background task via `BackgroundTasks`
  - [ ] Return 202 with OperationResponse

- [ ] Task 3: Tests for endpoint + task orchestration (AC: #1)

  - [ ] Add tests to `backend/tests/api/v1/test_sessions.py` (or create
        `test_sessions_feedback.py` if file is too large)
  - [ ] Mock OpenAI service / analysis service
  - [ ] Test:
    - [ ] 202 accepted and Operation created
    - [ ] 400 if session not completed
    - [ ] 409 if feedback exists
    - [ ] 404 if session not found/unauthorized
    - [ ] Operation transitions pending→processing→completed for success
    - [ ] Operation transitions pending→processing→failed for failure

## Dev Notes

### Critical Architecture Requirements

- **Async pattern (STRICT):** return 202 immediately; do not block request
  waiting for OpenAI.
- **Operation lifecycle:** pending → processing → completed|failed.
- **Authorization:** every access validated via `get_current_user` and
  `session.user_id == current_user.id`.
- **Idempotency behavior:** if feedback already exists, return 409 (do not
  regenerate).

### Technical Implementation Details

**Suggested files:**

```
backend/app/api/v1/endpoints/sessions.py   # UPDATE
backend/app/tasks/feedback_tasks.py        # NEW
backend/app/services/feedback_analysis_service.py  # EXISTS from 5.2
backend/tests/api/v1/test_sessions.py      # UPDATE
```

**Endpoint sketch (align with existing `generate-question` approach in
`sessions.py`):**

```python
@router.post(
    "/{session_id}/generate-feedback",
    response_model=OperationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate AI feedback for a completed session",
)
async def generate_feedback(
    session_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = await session_service.get_session_by_id(db, session_id, current_user)

    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "SESSION_NOT_COMPLETED", "message": "Session must be completed before feedback can be generated"},
        )

    # Check existing feedback (story 5.1 model)
    if await feedback_service.feedback_exists(db, session_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "FEEDBACK_ALREADY_EXISTS", "message": "Feedback already exists for this session"},
        )

    operation = Operation(operation_type="feedback_analysis", status="pending")
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    background_tasks.add_task(generate_feedback_task, operation.id, session_id, current_user.id)

    return OperationResponse.model_validate(operation)
```

### References

- Existing async operation patterns:
  - `backend/app/tasks/question_tasks.py`
  - `backend/app/models/operation.py`
  - `backend/app/api/v1/endpoints/operations.py`
- Similar endpoint style: `backend/app/api/v1/endpoints/sessions.py`
  generate-question

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

- Endpoint returns 202 immediately
- Operation state transitions verified
- 409 returned when feedback exists

### File List

_To be filled by dev agent_
