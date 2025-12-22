# Story 4.10: Store Generated Question as Session Message

Status: ready-for-dev

## Story

As a developer, I want to save successfully generated questions to the session,
so that we persist the conversation history.

## Acceptance Criteria

1. **Given** a question generation operation completes successfully **When** the
   background task finishes **Then** it creates a SessionMessage record with
   session_id, message_type='question', content=(generated question text),
   question_type=(technical/behavioral/situational) **And** increments the
   session's current_question_number **And** stores the question text in the
   Operation result field **And** uses UTC timestamps

## Tasks / Subtasks

- [ ] Task 1: Update question generation background task (AC: #1)

  - [ ] Modify `backend/app/tasks/question_tasks.py` generate_question_task
  - [ ] After successful question generation, create SessionMessage record
  - [ ] Set message_type='question'
  - [ ] Set content to generated question text
  - [ ] Set question_type from generation result
  - [ ] Set session_id to current session
  - [ ] Commit SessionMessage to database

- [ ] Task 2: Increment session question number (AC: #1)

  - [ ] After creating SessionMessage, update InterviewSession
  - [ ] Increment current_question_number by 1
  - [ ] Update session's updated_at timestamp (automatic via onupdate)
  - [ ] Commit session update to database

- [ ] Task 3: Ensure atomic operation (AC: #1)

  - [ ] Wrap SessionMessage creation and session update in transaction
  - [ ] If either fails, rollback both changes
  - [ ] Update Operation status to 'failed' if transaction fails
  - [ ] Log transaction errors with context

- [ ] Task 4: Add comprehensive tests (AC: #1)
  - [ ] Update `backend/tests/tasks/test_question_tasks.py`
  - [ ] Test successful generation creates SessionMessage
  - [ ] Test SessionMessage has correct fields (type, content, question_type)
  - [ ] Test session current_question_number increments
  - [ ] Test Operation result contains question data
  - [ ] Test transaction rollback on failure
  - [ ] Test multiple questions create separate messages

## Dev Notes

### Critical Architecture Requirements

**Database Transaction Pattern (CRITICAL):**

- SessionMessage creation and session update must be atomic
- If either fails, rollback both
- Update Operation status regardless of transaction outcome
- Use database transaction boundaries properly

**Message Creation:**

- message_type = 'question' (not 'answer')
- content = full question text from AI
- question_type = technical/behavioral/situational from generation
- session_id = foreign key to current session
- created_at = UTC timestamp (automatic)

**Session State Update:**

- current_question_number increments by 1
- Represents "next question to ask" or "total questions asked"
- Used by question type rotation logic (story 4.7)
- updated_at timestamp updated automatically

### Technical Implementation Details

**File Structure:**

```
backend/app/
└── tasks/
    └── question_tasks.py        # UPDATE - Add message creation
```

**Updated Background Task:**

```python
# backend/app/tasks/question_tasks.py
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.operation import Operation
from app.models.interview_session import InterviewSession
from app.models.session_message import SessionMessage
from app.models.user import User
from app.services.question_generation_service import generate_question
from app.core.database import get_db_session

logger = logging.getLogger(__name__)

async def generate_question_task(operation_id: UUID, session_id: UUID):
    """
    Background task to generate an interview question and store it.

    Args:
        operation_id: UUID of the Operation to update
        session_id: UUID of the InterviewSession
    """
    async with get_db_session() as db:
        try:
            # Load operation
            result = await db.execute(
                select(Operation).where(Operation.id == operation_id)
            )
            operation = result.scalar_one_or_none()

            if not operation:
                logger.error(f"Operation {operation_id} not found")
                return

            # Update to processing
            operation.status = "processing"
            await db.commit()

            # Load session with relationships
            result = await db.execute(
                select(InterviewSession)
                .where(InterviewSession.id == session_id)
                .options(
                    selectinload(InterviewSession.job_posting),
                    selectinload(InterviewSession.user).selectinload(User.resume)
                )
            )
            session = result.scalar_one_or_none()

            if not session:
                logger.error(f"Session {session_id} not found")
                operation.status = "failed"
                operation.error_message = "Session not found"
                await db.commit()
                return

            # Generate question
            question_data = await generate_question(session)

            # Store question as SessionMessage (atomic with session update)
            try:
                # Create message record
                message = SessionMessage(
                    session_id=session.id,
                    message_type="question",
                    content=question_data["question_text"],
                    question_type=question_data["question_type"]
                )
                db.add(message)

                # Increment session question number
                session.current_question_number += 1

                # Commit both changes atomically
                await db.commit()
                await db.refresh(message)

                logger.info(
                    f"Question stored as message {message.id} for session {session_id}, "
                    f"question number now {session.current_question_number}"
                )

            except Exception as db_error:
                logger.error(f"Failed to store question in session {session_id}: {str(db_error)}")
                await db.rollback()

                operation.status = "failed"
                operation.error_message = "Failed to store question in database"
                await db.commit()
                return

            # Update operation with result
            operation.status = "completed"
            operation.result = question_data
            await db.commit()

            logger.info(f"Question generated and stored successfully for operation {operation_id}")

        except Exception as e:
            logger.error(f"Error in question generation task {operation_id}: {str(e)}", exc_info=True)

            # Update operation with error
            try:
                operation.status = "failed"
                operation.error_message = str(e)
                await db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update operation {operation_id} with error: {commit_error}")
```

**Testing Patterns:**

```python
# backend/tests/tasks/test_question_tasks.py
import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.tasks.question_tasks import generate_question_task
from app.models.operation import Operation
from app.models.interview_session import InterviewSession
from app.models.session_message import SessionMessage

@pytest.mark.asyncio
@patch('app.tasks.question_tasks.generate_question')
async def test_question_task_creates_message(
    mock_generate,
    db: AsyncSession,
    test_session: InterviewSession
):
    """Test task creates SessionMessage after generating question."""
    mock_generate.return_value = {
        "question_text": "What is your experience with Python?",
        "question_type": "technical"
    }

    # Create operation
    operation = Operation(
        operation_type="question_generation",
        status="pending"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    initial_question_number = test_session.current_question_number

    # Run task
    await generate_question_task(operation.id, test_session.id)

    # Verify message created
    result = await db.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == test_session.id,
            SessionMessage.message_type == "question"
        )
    )
    message = result.scalar_one_or_none()

    assert message is not None
    assert message.content == "What is your experience with Python?"
    assert message.question_type == "technical"

    # Verify session updated
    await db.refresh(test_session)
    assert test_session.current_question_number == initial_question_number + 1

@pytest.mark.asyncio
@patch('app.tasks.question_tasks.generate_question')
async def test_question_task_updates_operation(
    mock_generate,
    db: AsyncSession,
    test_session: InterviewSession
):
    """Test task updates operation with completed status."""
    mock_generate.return_value = {
        "question_text": "Test question",
        "question_type": "behavioral"
    }

    operation = Operation(
        operation_type="question_generation",
        status="pending"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    await generate_question_task(operation.id, test_session.id)

    # Verify operation completed
    await db.refresh(operation)
    assert operation.status == "completed"
    assert operation.result["question_text"] == "Test question"

@pytest.mark.asyncio
@patch('app.tasks.question_tasks.generate_question')
async def test_question_task_handles_failure(
    mock_generate,
    db: AsyncSession,
    test_session: InterviewSession
):
    """Test task handles generation failure gracefully."""
    mock_generate.side_effect = Exception("OpenAI error")

    operation = Operation(
        operation_type="question_generation",
        status="pending"
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    initial_question_number = test_session.current_question_number

    await generate_question_task(operation.id, test_session.id)

    # Verify operation failed
    await db.refresh(operation)
    assert operation.status == "failed"
    assert "OpenAI error" in operation.error_message

    # Verify no message created
    result = await db.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == test_session.id
        )
    )
    messages = result.scalars().all()
    assert len(messages) == 0

    # Verify session not updated
    await db.refresh(test_session)
    assert test_session.current_question_number == initial_question_number

@pytest.mark.asyncio
@patch('app.tasks.question_tasks.generate_question')
async def test_multiple_questions_increment_correctly(
    mock_generate,
    db: AsyncSession,
    test_session: InterviewSession
):
    """Test multiple questions increment session number correctly."""
    questions = [
        {"question_text": "Question 1", "question_type": "technical"},
        {"question_text": "Question 2", "question_type": "behavioral"},
        {"question_text": "Question 3", "question_type": "situational"}
    ]

    for i, q_data in enumerate(questions):
        mock_generate.return_value = q_data

        operation = Operation(
            operation_type="question_generation",
            status="pending"
        )
        db.add(operation)
        await db.commit()
        await db.refresh(operation)

        await generate_question_task(operation.id, test_session.id)

        await db.refresh(test_session)
        assert test_session.current_question_number == i + 1

    # Verify all messages created
    result = await db.execute(
        select(SessionMessage).where(
            SessionMessage.session_id == test_session.id
        ).order_by(SessionMessage.created_at)
    )
    messages = result.scalars().all()
    assert len(messages) == 3
```

### Dependencies

- Requires SessionMessage model from story 4.1
- Requires InterviewSession model from story 4.1
- Requires Operation model from story 4.5
- Requires question_generation_service from story 4.7
- Requires background task from story 4.8

### Related Stories

- Story 4.1: Created SessionMessage model
- Story 4.7: Generates question content
- Story 4.8: Background task framework (updated here)
- Story 4.12: Retrieves messages (reads what this creates)

### Performance Considerations

- Single transaction for message + session update (fast)
- Indexes on session_id and created_at from story 4.1
- Minimal data written (< 1KB per message)
- Transaction locks brief (microseconds)

### Data Integrity

- Atomic operation ensures consistency
- If message creation fails, question number doesn't increment
- If session update fails, message creation rolled back
- Operation status always reflects true state

### Design Decisions

**Why store in Operation result AND SessionMessage?**

- Operation result: Immediate response to frontend poll
- SessionMessage: Persistent conversation history
- Operation may be deleted eventually (cleanup)
- SessionMessage is permanent record

**Why increment question_number?**

- Tracks session progress
- Used for question type rotation (story 4.7)
- Enables "Question 3 of 10" UI display
- Simple counter, not complex state machine

**Why atomic transaction?**

- Prevents orphaned messages
- Prevents incorrect question numbers
- Ensures data consistency
- Simplifies error handling

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Transaction patterns, atomicity
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR34, NFR-R2 (immediate save, zero data loss)

**Key Context Sections:**

- Database Patterns: Transactions, rollback, atomicity
- Error Handling: Transaction failure recovery
- Testing: Testing async transactions
