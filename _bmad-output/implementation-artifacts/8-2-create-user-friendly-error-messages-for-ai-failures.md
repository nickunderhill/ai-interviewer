# Story 8.2: Create User-Friendly Error Messages for AI Failures

Status: done

## Story

As a user, I want to see clear, actionable error messages when AI operations
fail, so that I understand what went wrong and what to do next.

## Acceptance Criteria

1. **Given** an AI operation (question generation or feedback analysis) fails
   **When** I check the operation status **Then** the error_message field
   contains user-friendly text like "Unable to generate question. Please check
   your OpenAI API key configuration." or "Question generation is taking longer
   than expected. Please try again." **And** the message avoids technical jargon
   and API details **And** provides actionable next steps (e.g., "Check API
   key", "Try again later", "Contact support") **And** the frontend displays
   these messages prominently **And** the UI provides a retry button where
   appropriate (FR59, FR64) ✅

## Tasks / Subtasks

- [x] Task 1: Create error message mapping system (AC: #1)

  - [x] Define error_code to user-friendly message mappings
  - [x] Create `backend/app/utils/error_messages.py` with mapping dictionary
  - [x] Include actionable next steps for each error type
  - [x] Support dynamic variables (e.g., operation type, retry count)

- [x] Task 2: Update Operation model to store user-friendly messages (AC: #1)

  - [x] Verify Operation model has error_message field (should exist from 4-5)
  - [x] Ensure error_message is nullable and stored as Text/String
  - [x] Update operation creation to include user-friendly messages
  - [x] Add index on operation status for efficient querying

- [x] Task 3: Implement error message generation service (AC: #1)

  - [x] Create `generate_user_friendly_message(error_code, context)` function
  - [x] Map technical error codes to user messages
  - [x] Include dynamic context (e.g., operation type, session info)
  - [x] Ensure no sensitive data (API keys, internal errors) in messages

- [x] Task 4: Update background tasks to set user-friendly error messages (AC:
      #1)

  - [x] Update question generation task error handling
  - [x] Update feedback analysis task error handling
  - [x] Set Operation.error_message with user-friendly text on failure
  - [x] Log technical error details separately for debugging

- [x] Task 5: Create frontend error display component (AC: #1)

  - [x] Create `ErrorDisplay.tsx` component in `frontend/src/components/common/`
  - [x] Display error message prominently with error icon
  - [x] Show actionable next steps as bullet points or buttons
  - [x] Include retry button for retriable operations
  - [x] Use Tailwind CSS for styling (red/orange theme)

- [x] Task 6: Integrate error display in session and feedback views (AC: #1)
  - [x] Update SessionDetail view to show operation errors
  - [x] Update FeedbackView to display analysis errors
  - [x] Show error messages inline near failed operations
  - [x] Provide retry functionality where applicable

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Error Messages:** User-friendly, actionable, no technical jargon
- **Context Awareness:** Messages tailored to operation type (question gen vs.
  feedback)
- **Security:** Never expose API keys, internal errors, or sensitive data
- **Persistence:** Store error messages in Operation model for retrieval

**Frontend:**

- **Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS v3+ for consistent error UI
- **State:** TanStack Query for operation status polling
- **Component Location:** `frontend/src/components/common/ErrorDisplay.tsx`

### File Structure

```
backend/app/
├── utils/
│   └── error_messages.py      # Error code to user-friendly message mappings
├── services/
│   ├── question_generation.py # Update to use user-friendly messages
│   └── feedback_analysis.py   # Update to use user-friendly messages
└── api/v1/endpoints/
    └── operations.py          # Return error_message in response

frontend/src/
├── components/
│   └── common/
│       └── ErrorDisplay.tsx   # Reusable error display component
└── features/
    ├── sessions/
    │   └── components/
    │       └── SessionDetail.tsx  # Show operation errors
    └── feedback/
        └── components/
            └── FeedbackView.tsx   # Show analysis errors
```

### Implementation Details

**Error Message Mapping:**

```python
# backend/app/utils/error_messages.py
from typing import Dict, Optional

ERROR_MESSAGES: Dict[str, Dict[str, any]] = {
    "INVALID_API_KEY": {
        "message": "Unable to connect to AI service. Your OpenAI API key appears to be invalid.",
        "action": "Please check your API key configuration in your profile settings.",
        "retriable": False,
        "severity": "error"
    },
    "RATE_LIMIT_EXCEEDED": {
        "message": "AI service rate limit reached. Please wait a moment before trying again.",
        "action": "This is temporary. You can retry in a few seconds.",
        "retriable": True,
        "severity": "warning"
    },
    "QUOTA_EXCEEDED": {
        "message": "Your OpenAI account has exceeded its quota.",
        "action": "Please check your OpenAI account billing and usage at https://platform.openai.com/account/usage",
        "retriable": False,
        "severity": "error"
    },
    "NETWORK_ERROR": {
        "message": "Unable to reach AI service due to network issues.",
        "action": "Please check your internet connection and try again.",
        "retriable": True,
        "severity": "warning"
    },
    "SERVER_ERROR": {
        "message": "AI service is temporarily unavailable.",
        "action": "This is usually temporary. Please try again in a few moments.",
        "retriable": True,
        "severity": "warning"
    },
    "TIMEOUT": {
        "message": "AI operation took too long and was cancelled.",
        "action": "Please try again. If this persists, the request may be too complex.",
        "retriable": True,
        "severity": "warning"
    },
    "INVALID_RESPONSE": {
        "message": "Received unexpected response from AI service.",
        "action": "Please try again. If this persists, contact support.",
        "retriable": True,
        "severity": "error"
    },
    "MISSING_API_KEY": {
        "message": "No OpenAI API key configured.",
        "action": "Please add your OpenAI API key in your profile settings to use AI features.",
        "retriable": False,
        "severity": "error"
    }
}

def generate_user_friendly_message(
    error_code: str,
    operation_type: Optional[str] = None,
    context: Optional[Dict] = None
) -> str:
    """
    Generate user-friendly error message from error code.

    Args:
        error_code: Internal error code (e.g., "INVALID_API_KEY")
        operation_type: Type of operation (e.g., "question_generation", "feedback_analysis")
        context: Additional context for message customization

    Returns:
        Formatted user-friendly error message with actionable steps
    """
    error_info = ERROR_MESSAGES.get(error_code, {
        "message": "An unexpected error occurred.",
        "action": "Please try again. If the problem persists, contact support.",
        "retriable": True,
        "severity": "error"
    })

    # Customize message based on operation type
    operation_context = ""
    if operation_type == "question_generation":
        operation_context = " generating your interview question"
    elif operation_type == "feedback_analysis":
        operation_context = " analyzing your answer"

    full_message = f"{error_info['message'].replace('.', operation_context + '.')}\n\n"
    full_message += f"What to do: {error_info['action']}"

    return full_message

def is_retriable(error_code: str) -> bool:
    """Check if error is retriable."""
    error_info = ERROR_MESSAGES.get(error_code, {})
    return error_info.get("retriable", False)

def get_error_severity(error_code: str) -> str:
    """Get error severity level."""
    error_info = ERROR_MESSAGES.get(error_code, {})
    return error_info.get("severity", "error")
```

**Update Background Tasks:**

```python
# backend/app/services/question_generation.py (excerpt)
from app.utils.error_messages import generate_user_friendly_message
from app.core.exceptions import OpenAIError

async def generate_question_background(operation_id: str, session_id: str, db: AsyncSession):
    """Background task to generate question with user-friendly error messages."""
    try:
        # ... existing question generation logic ...

    except OpenAIError as e:
        # Generate user-friendly error message
        user_message = generate_user_friendly_message(
            error_code=e.error_code,
            operation_type="question_generation",
            context={"session_id": session_id}
        )

        # Update operation with user-friendly message
        async with db.begin():
            operation = await db.get(Operation, operation_id)
            operation.status = "failed"
            operation.error_message = user_message
            await db.commit()

        # Log technical details separately
        logger.error(
            "Question generation failed",
            extra={
                "operation_id": operation_id,
                "session_id": session_id,
                "error_code": e.error_code,
                "technical_error": str(e.original_error)
            }
        )
```

**Frontend Error Display Component:**

```tsx
// frontend/src/components/common/ErrorDisplay.tsx
import { AlertCircle, RefreshCw } from 'lucide-react';

interface ErrorDisplayProps {
  message: string;
  onRetry?: () => void;
  severity?: 'error' | 'warning' | 'info';
}

export function ErrorDisplay({
  message,
  onRetry,
  severity = 'error',
}: ErrorDisplayProps) {
  const severityStyles = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-orange-50 border-orange-200 text-orange-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  };

  const iconStyles = {
    error: 'text-red-600',
    warning: 'text-orange-600',
    info: 'text-blue-600',
  };

  // Split message into main message and action (separated by "What to do:")
  const [mainMessage, actionText] = message.split('What to do:');

  return (
    <div className={`border rounded-lg p-4 ${severityStyles[severity]}`}>
      <div className="flex items-start gap-3">
        <AlertCircle
          className={`h-5 w-5 mt-0.5 flex-shrink-0 ${iconStyles[severity]}`}
        />
        <div className="flex-1">
          <p className="font-medium mb-2">{mainMessage.trim()}</p>
          {actionText && (
            <p className="text-sm mb-3">
              <strong>What to do:</strong> {actionText.trim()}
            </p>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm font-medium"
            >
              <RefreshCw className="h-4 w-4" />
              Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Integration in SessionDetail:**

```tsx
// frontend/src/features/sessions/components/SessionDetail.tsx (excerpt)
import { ErrorDisplay } from '@/components/common/ErrorDisplay';
import { useRetryOperation } from '../hooks/useRetryOperation';

function SessionDetail({ sessionId }: { sessionId: string }) {
  const { data: operation } = useQuery(['operation', operationId]);
  const retryMutation = useRetryOperation();

  if (operation?.status === 'failed' && operation.error_message) {
    return (
      <ErrorDisplay
        message={operation.error_message}
        onRetry={() => retryMutation.mutate(operation.id)}
        severity="error"
      />
    );
  }

  // ... rest of component ...
}
```

### Testing Requirements

**Test Coverage:**

- All error codes map to user-friendly messages
- Messages are clear and actionable
- No technical jargon or sensitive data in messages
- Frontend displays errors prominently
- Retry button appears for retriable errors

**Test Files:**

- `backend/tests/utils/test_error_messages.py`
- `backend/tests/services/test_question_generation_errors.py`
- `frontend/src/components/common/ErrorDisplay.test.tsx`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.2]
- [Source: _bmad-output/project-context.md#Error-Handling]
- [FR59: Display processing status during question generation]
- [FR64: User-friendly error handling]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Implemented comprehensive backend error message mapping system
- User-friendly messages include actionable next steps and avoid sensitive data
- Background tasks persist user-friendly `Operation.error_message` on failures
- Full backend test suite passing
- Added reusable frontend `ErrorDisplay` component with tests
- Added operation polling + retry error display in SessionDetail and
  FeedbackView
- Frontend test suite passing

### Implementation Notes

- Implemented `backend/app/utils/error_messages.py` with
  `ERROR_MESSAGE_TEMPLATES` and `render_template()`.
- Added backend unit tests validating required codes and dynamic rendering.
- Verified Operation model already supports `error_message` persistence and
  status indexing; added regression test coverage.
- Added `generate_user_friendly_message()` backed by templates, with secret
  masking and safe context normalization.
- Updated background tasks to set `Operation.error_message` to user-friendly
  messages (instead of raw exception text), including session-not-found, DB
  failures, and AI failures.
- Updated API and task tests to assert the user-friendly messages and avoid
  leaking raw exception details.

## File List

- backend/app/utils/error_messages.py
- backend/app/tasks/question_tasks.py
- backend/app/tasks/feedback_tasks.py
- backend/tests/utils/test_error_messages.py
- backend/tests/test_operation_model.py
- backend/tests/tasks/test_question_tasks.py
- backend/tests/tasks/test_feedback_tasks.py
- backend/tests/api/v1/test_sessions_generate_question.py
- frontend/src/components/common/ErrorDisplay.tsx
- frontend/src/components/common/**tests**/ErrorDisplay.test.tsx
- frontend/src/services/operationsApi.ts
- frontend/src/services/sessionAiApi.ts
- frontend/src/features/sessions/components/SessionDetail.tsx
- frontend/src/features/sessions/components/**tests**/SessionDetail.test.tsx
- frontend/src/App.tsx
- frontend/src/features/feedback/api/feedbackApi.ts
- frontend/src/features/feedback/components/FeedbackView.tsx
- frontend/src/features/feedback/components/**tests**/FeedbackView.test.tsx

## Change Log

- 2025-12-26: Completed Task 1 (backend error message template mapping + tests)
- 2025-12-26: Completed Task 2 (verified Operation.error_message schema +
  indexing; added regression test)
- 2025-12-26: Completed Task 3 (user-friendly error message generation + tests)
- 2025-12-26: Completed Task 4 (background tasks now persist user-friendly
  Operation.error_message; updated tests; full backend regression passing)
- 2025-12-26: Completed Task 5 (frontend ErrorDisplay component + unit tests)
- 2025-12-26: Completed Task 6 (SessionDetail and FeedbackView display operation
  failures via ErrorDisplay with retry; added operation polling services and
  feedback route; frontend tests passing)
