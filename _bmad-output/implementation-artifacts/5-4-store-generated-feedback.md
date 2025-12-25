# Story 5.4: Store Generated Feedback

Status: ready-for-dev

## Story

As a developer, I want to save successfully generated feedback to the database,
so that we persist the analysis for future retrieval.

## Acceptance Criteria

1. **Given** a feedback generation operation completes successfully **When** the
   background task finishes **Then** it creates an InterviewFeedback record with
   all dimension scores, feedback text, knowledge_gaps array, and
   learning_recommendations array **And** calculates overall_score as the
   average of the 4 dimension scores **And** links to the session via session_id
   **And** stores the complete feedback in the Operation result field **And**
   uses UTC timestamps

## Tasks / Subtasks

- [ ] Task 1: Implement persistence inside background task (AC: #1)

  - [ ] Update `backend/app/tasks/feedback_tasks.py` (from story 5.3)
  - [ ] On successful analysis result:
    - [ ] Compute `overall_score = round((a+b+c+d)/4)` (document rounding
          strategy)
    - [ ] Create `InterviewFeedback` ORM object (story 5.1)
    - [ ] Save to DB and commit
    - [ ] Update Operation:
      - [ ] `status='completed'`
      - [ ] `result=<full JSON including overall_score>`

- [ ] Task 2: Prevent duplicates and handle races (AC: #1)

  - [ ] Enforce DB uniqueness on feedback.session_id (story 5.1)
  - [ ] In task, handle IntegrityError on duplicate insert:
    - [ ] set Operation failed with `FEEDBACK_ALREADY_EXISTS`
    - [ ] or treat as success (choose one; acceptance criteria suggests conflict
          earlier, but races can still happen)

- [ ] Task 3: Tests for persistence logic (AC: #1)

  - [ ] Add unit/integration tests:
    - [ ] successful background run creates InterviewFeedback row
    - [ ] overall_score calculated correctly
    - [ ] Operation.result mirrors stored feedback
    - [ ] duplicate creation behavior deterministic

## Dev Notes

### Critical Architecture Requirements

- **Atomicity:** feedback + operation updates must leave system in consistent
  state.
- **UTC timestamps:** stored and returned timezone-aware.
- **No leakage:** Operation.result may contain résumé and transcript-derived
  content; do not include sensitive user secrets.

### Technical Implementation Details

**Suggested files:**

```
backend/app/tasks/feedback_tasks.py              # UPDATE
backend/app/models/interview_feedback.py         # EXISTS (5.1)
backend/tests/services/test_feedback_tasks.py    # NEW (or add to sessions tests)
```

**Overall score rule:**

- Use average of 4 dimension scores:

$$ overall_score = \text{round}\left(\frac{s_1+s_2+s_3+s_4}{4}\right) $$

Document rounding: `round()` vs floor vs int-cast.

**Pseudo-flow:**

1. Set Operation → processing
2. Call analysis service → get result
3. Compute overall_score
4. Insert InterviewFeedback(session_id=..., ...)
5. Set Operation → completed + result JSON

### References

- [Operation patterns:
  _bmad-output/implementation-artifacts/4-5-create-operation-model-for-long-running-ai-tasks.md]
- [Question background task pattern: backend/app/tasks/question_tasks.py]

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

- Feedback stored with one-to-one session mapping
- overall_score computed consistently
- Operation.result stores full feedback

### File List

_To be filled by dev agent_
