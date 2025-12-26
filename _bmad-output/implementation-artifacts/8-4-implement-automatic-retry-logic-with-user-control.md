# Story 8.4: Implement Automatic Retry Logic with User Control

Status: ready-for-dev

## Story

As a user, I want the system to automatically retry failed AI requests, and have
the option to manually retry, so that transient failures are handled without my
intervention.

## Acceptance Criteria

1. **Given** an AI operation fails due to a transient error (network timeout,
   5xx) **When** the background task detects the failure **Then** it
   automatically retries up to 3 times with exponential backoff (1s, 2s, 4s)
   **And** if all retries fail, marks the Operation as 'failed' **And** the user
   sees a "Retry" button in the UI **And** clicking Retry initiates a new
   operation (new operation_id) **And** the retry attempt is logged **And**
   users are never blocked indefinitely by failures (FR61) ✅

## Tasks / Subtasks

- [ ] Task 1: Verify automatic retry is implemented in OpenAI service (AC: #1)

  - [ ] Check Story 8.1 retry decorator is applied
  - [ ] Verify exponential backoff (1s, 2s, 4s) with jitter
  - [ ] Confirm only transient errors trigger retry
  - [ ] Ensure retry attempts are logged

- [ ] Task 2: Create manual retry endpoint (AC: #1)

  - [ ] POST `/api/v1/operations/{id}/retry` endpoint
  - [ ] Validate operation exists and is in 'failed' state
  - [ ] Create new operation with same parameters
  - [ ] Return new operation_id to client
  - [ ] Log retry attempt with original operation context

- [ ] Task 3: Update Operation model to track retry history (AC: #1)

  - [ ] Add optional `parent_operation_id` field (nullable UUID)
  - [ ] Add `retry_count` field (default 0)
  - [ ] Create foreign key relationship to parent operation
  - [ ] Migration to add new fields

- [ ] Task 4: Implement retry service logic (AC: #1)

  - [ ] Create `retry_operation(operation_id)` function
  - [ ] Fetch original operation details
  - [ ] Determine operation type (question_generation vs feedback_analysis)
  - [ ] Create new operation with same parameters
  - [ ] Set parent_operation_id and increment retry_count
  - [ ] Trigger background task for new operation

- [ ] Task 5: Create frontend retry hook (AC: #1)

  - [ ] Create `useRetryOperation` mutation hook
  - [ ] Call POST `/api/v1/operations/{id}/retry`
  - [ ] Invalidate relevant queries on success
  - [ ] Handle retry errors gracefully
  - [ ] Show success/error toast notifications

- [ ] Task 6: Add retry button to error displays (AC: #1)
  - [ ] Update ErrorDisplay component to accept onRetry prop
  - [ ] Show retry button only for failed operations
  - [ ] Disable button during retry request
  - [ ] Show loading state while retrying
  - [ ] Update UI when new operation starts

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Automatic Retry:** Already implemented in Story 8.1 (exponential backoff)
- **Manual Retry:** New endpoint creates fresh operation
- **Operation Tracking:** Parent-child relationship for retry history
- **Idempotency:** Each retry is a new operation_id

**Frontend:**

- **Framework:** React 18+ with TypeScript
- **State:** TanStack Query for mutations
- **UI:** Retry button in ErrorDisplay component
- **Feedback:** Toast notifications for retry status

### File Structure

```
backend/app/
├── models/
│   └── operation.py           # Add parent_operation_id, retry_count fields
├── api/v1/endpoints/
│   └── operations.py          # Add retry endpoint
├── services/
│   └── operation_service.py   # Retry logic
└── alembic/versions/
    └── xxxx_add_retry_fields.py  # Migration

frontend/src/
├── features/
│   └── sessions/
│       └── hooks/
│           └── useRetryOperation.ts  # Retry mutation hook
└── components/
    └── common/
        └── ErrorDisplay.tsx   # Update with retry button
```

### Implementation Details

**Operation Model Update:**

```python
# backend/app/models/operation.py
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

class OperationStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Operation(Base):
    __tablename__ = "operations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    operation_type = Column(String, nullable=False)  # question_generation, feedback_analysis
    status = Column(Enum(OperationStatus), nullable=False, default=OperationStatus.PENDING)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Retry tracking
    parent_operation_id = Column(UUID(as_uuid=True), ForeignKey("operations.id"), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    # Relationships
    parent = relationship("Operation", remote_side=[id], backref="retries")

    # Context (varies by operation type)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id"), nullable=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("session_messages.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**Retry Endpoint:**

```python
# backend/app/api/v1/endpoints/operations.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.operation_service import retry_operation
from app.core.deps import get_db, get_current_user
from app.schemas.operation import OperationResponse

router = APIRouter()

@router.post("/{operation_id}/retry", response_model=OperationResponse)
async def retry_operation_endpoint(
    operation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually retry a failed operation.
    Creates a new operation with the same parameters.
    """
    try:
        new_operation = await retry_operation(
            operation_id=operation_id,
            user_id=current_user.id,
            db=db
        )
        return new_operation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Retry operation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry operation"
        )
```

**Retry Service:**

```python
# backend/app/services/operation_service.py
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.operation import Operation
from app.models.session import InterviewSession
from app.models.message import SessionMessage
from app.services.question_generation import generate_question_background
from app.services.feedback_analysis import analyze_feedback_background

logger = logging.getLogger(__name__)

async def retry_operation(
    operation_id: str,
    user_id: str,
    db: AsyncSession
) -> Operation:
    """
    Retry a failed operation by creating a new one with same parameters.

    Args:
        operation_id: UUID of the failed operation
        user_id: Current user ID for authorization
        db: Database session

    Returns:
        New Operation instance

    Raises:
        ValueError: If operation not found, not failed, or user unauthorized
    """
    # Fetch original operation
    result = await db.execute(
        select(Operation).where(Operation.id == operation_id)
    )
    original_op = result.scalar_one_or_none()

    if not original_op:
        raise ValueError("Operation not found")

    if original_op.status != "failed":
        raise ValueError("Can only retry failed operations")

    # Verify user authorization
    if original_op.session_id:
        session_result = await db.execute(
            select(InterviewSession).where(InterviewSession.id == original_op.session_id)
        )
        session = session_result.scalar_one_or_none()
        if not session or session.user_id != user_id:
            raise ValueError("Unauthorized to retry this operation")

    # Create new operation
    new_operation = Operation(
        operation_type=original_op.operation_type,
        status="pending",
        session_id=original_op.session_id,
        message_id=original_op.message_id,
        parent_operation_id=original_op.id,
        retry_count=original_op.retry_count + 1
    )

    db.add(new_operation)
    await db.commit()
    await db.refresh(new_operation)

    # Trigger background task based on operation type
    if original_op.operation_type == "question_generation":
        asyncio.create_task(
            generate_question_background(
                operation_id=str(new_operation.id),
                session_id=str(original_op.session_id),
                db=db
            )
        )
    elif original_op.operation_type == "feedback_analysis":
        asyncio.create_task(
            analyze_feedback_background(
                operation_id=str(new_operation.id),
                message_id=str(original_op.message_id),
                db=db
            )
        )

    logger.info(
        "Operation retry initiated",
        extra={
            "original_operation_id": str(original_op.id),
            "new_operation_id": str(new_operation.id),
            "retry_count": new_operation.retry_count,
            "operation_type": original_op.operation_type
        }
    )

    return new_operation
```

**Frontend Retry Hook:**

```typescript
// frontend/src/features/sessions/hooks/useRetryOperation.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { retryOperation } from '@/services/api';
import { toast } from 'react-hot-toast';

export function useRetryOperation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (operationId: string) => retryOperation(operationId),
    onSuccess: newOperation => {
      toast.success('Retrying operation...');

      // Invalidate relevant queries
      queryClient.invalidateQueries(['operation', newOperation.id]);
      if (newOperation.session_id) {
        queryClient.invalidateQueries(['session', newOperation.session_id]);
      }
    },
    onError: (error: any) => {
      const message =
        error.response?.data?.detail || 'Failed to retry operation';
      toast.error(message);
    },
  });
}
```

**API Service Function:**

```typescript
// frontend/src/services/api.ts (add this function)
export async function retryOperation(operationId: string): Promise<Operation> {
  const response = await apiClient.post(
    `/api/v1/operations/${operationId}/retry`
  );
  return response.data;
}
```

**Updated ErrorDisplay Component:**

```tsx
// frontend/src/components/common/ErrorDisplay.tsx (update)
import { AlertCircle, RefreshCw } from 'lucide-react';
import { useState } from 'react';

interface ErrorDisplayProps {
  message: string;
  operationId?: string;
  onRetry?: (operationId: string) => void;
  severity?: 'error' | 'warning' | 'info';
}

export function ErrorDisplay({
  message,
  operationId,
  onRetry,
  severity = 'error',
}: ErrorDisplayProps) {
  const [isRetrying, setIsRetrying] = useState(false);

  const handleRetry = async () => {
    if (onRetry && operationId) {
      setIsRetrying(true);
      try {
        await onRetry(operationId);
      } finally {
        setIsRetrying(false);
      }
    }
  };

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
          {onRetry && operationId && (
            <button
              onClick={handleRetry}
              disabled={isRetrying}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw
                className={`h-4 w-4 ${isRetrying ? 'animate-spin' : ''}`}
              />
              {isRetrying ? 'Retrying...' : 'Retry'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
```

### Testing Requirements

**Test Coverage:**

- Automatic retry works with exponential backoff (Story 8.1)
- Manual retry creates new operation with correct parent_id
- Retry endpoint validates authorization
- Frontend retry hook invalidates correct queries
- Retry button shows loading state

**Test Files:**

- `backend/tests/api/v1/test_operations_retry.py`
- `backend/tests/services/test_operation_service.py`
- `frontend/src/features/sessions/hooks/useRetryOperation.test.ts`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.4]
- [Source: Story 8.1 - Automatic retry implementation]
- [FR61: Implement retry logic for transient failures]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with automatic and manual retry logic
- Operation model updated with retry tracking
- Frontend retry hook with toast notifications
- Ready for dev implementation
