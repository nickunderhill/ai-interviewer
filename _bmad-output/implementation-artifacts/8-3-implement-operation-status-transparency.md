# Story 8.3: Implement Operation Status Transparency

Status: ready-for-dev

## Story

As a user, I want to always see the current processing status of AI operations,
so that I know what's happening with my requests.

## Acceptance Criteria

1. **Given** I've initiated an AI operation **When** I view the relevant page
   (interview session or feedback) **Then** the frontend displays clear status
   indicators: "Generating question..." (pending/processing), "Question ready!"
   (completed), "Generation failed" (failed) **And** uses visual feedback
   (spinners, progress indicators, status badges) **And** the polling mechanism
   checks status every 2-3 seconds and updates the UI in real-time **And** the
   user never sees stale or unclear states **And** if an operation takes >30
   seconds, displays a message indicating it's still processing (FR58, FR60) ✅

## Tasks / Subtasks

- [ ] Task 1: Create operation status constants and types (AC: #1)

  - [ ] Define TypeScript types for operation statuses
  - [ ] Create status display text mapping
  - [ ] Define visual indicators for each status
  - [ ] Create status badge color schemes

- [ ] Task 2: Implement polling hook for operation status (AC: #1)

  - [ ] Create `useOperationPolling` custom hook
  - [ ] Poll every 2-3 seconds while status is 'pending' or 'processing'
  - [ ] Stop polling when status is 'completed' or 'failed'
  - [ ] Handle timeout after 30 seconds with warning message
  - [ ] Cleanup intervals on component unmount

- [ ] Task 3: Create status indicator components (AC: #1)

  - [ ] Create `OperationStatus.tsx` component
  - [ ] Show spinner for 'pending'/'processing' states
  - [ ] Show success checkmark for 'completed' state
  - [ ] Show error icon for 'failed' state
  - [ ] Add status text with appropriate colors
  - [ ] Include elapsed time display

- [ ] Task 4: Create loading state components (AC: #1)

  - [ ] Create `ProcessingIndicator.tsx` for AI operations
  - [ ] Animated spinner or progress bar
  - [ ] Display operation type (e.g., "Generating question...")
  - [ ] Show elapsed time after 10 seconds
  - [ ] Show "taking longer than expected" message after 30 seconds

- [ ] Task 5: Integrate status indicators in session views (AC: #1)

  - [ ] Update SessionDetail to show question generation status
  - [ ] Update AnswerForm to show analysis status after submission
  - [ ] Replace static loading states with real-time polling
  - [ ] Show status history for completed operations

- [ ] Task 6: Integrate status indicators in feedback views (AC: #1)

  - [ ] Update FeedbackView to show analysis status
  - [ ] Show real-time progress during feedback generation
  - [ ] Display completion status prominently
  - [ ] Handle timeout scenarios gracefully

- [ ] Task 7: Add operation status badges (AC: #1)
  - [ ] Create `StatusBadge.tsx` component
  - [ ] Color-coded badges (blue=processing, green=completed, red=failed)
  - [ ] Use Tailwind CSS for consistent styling
  - [ ] Accessible with ARIA labels

## Dev Notes

### Critical Architecture Requirements

**Frontend:**

- **Polling:** TanStack Query with refetchInterval for real-time updates
- **Framework:** React 18+ with TypeScript
- **Styling:** Tailwind CSS v3+ for status indicators
- **Icons:** Lucide React for spinner, checkmark, error icons
- **Accessibility:** ARIA labels and live regions for status updates

**Backend:**

- **Operation Model:** Status field with values: pending, processing, completed,
  failed
- **API Endpoint:** GET `/api/v1/operations/{id}` returns current status
- **Response Time:** <300ms for operation status endpoint

### File Structure

```
frontend/src/
├── components/
│   └── common/
│       ├── OperationStatus.tsx      # Status indicator component
│       ├── ProcessingIndicator.tsx  # Loading state component
│       └── StatusBadge.tsx          # Colored status badge
├── features/
│   └── sessions/
│       └── hooks/
│           └── useOperationPolling.ts  # Polling hook
└── types/
    └── operation.ts                 # Operation types and constants
```

### Implementation Details

**Operation Types:**

```typescript
// frontend/src/types/operation.ts
export type OperationStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface Operation {
  id: string;
  operation_type: 'question_generation' | 'feedback_analysis';
  status: OperationStatus;
  result?: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export const OPERATION_STATUS_DISPLAY: Record<OperationStatus, string> = {
  pending: 'Queued...',
  processing: 'Processing...',
  completed: 'Completed',
  failed: 'Failed',
};

export const OPERATION_TYPE_DISPLAY: Record<
  Operation['operation_type'],
  string
> = {
  question_generation: 'Generating question',
  feedback_analysis: 'Analyzing answer',
};
```

**Polling Hook:**

```typescript
// frontend/src/features/sessions/hooks/useOperationPolling.ts
import { useQuery } from '@tanstack/react-query';
import { useState, useEffect } from 'react';
import { getOperationStatus } from '@/services/api';
import type { Operation } from '@/types/operation';

export function useOperationPolling(operationId: string | null) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [showTimeoutWarning, setShowTimeoutWarning] = useState(false);

  const { data: operation, isLoading } = useQuery<Operation>(
    ['operation', operationId],
    () => getOperationStatus(operationId!),
    {
      enabled: !!operationId,
      refetchInterval: data => {
        // Stop polling if completed or failed
        if (!data || data.status === 'completed' || data.status === 'failed') {
          return false;
        }
        // Poll every 2-3 seconds
        return 2500;
      },
      refetchOnWindowFocus: false,
    }
  );

  // Track elapsed time
  useEffect(() => {
    if (
      !operationId ||
      operation?.status === 'completed' ||
      operation?.status === 'failed'
    ) {
      setElapsedSeconds(0);
      setShowTimeoutWarning(false);
      return;
    }

    const interval = setInterval(() => {
      setElapsedSeconds(prev => {
        const next = prev + 1;
        if (next === 30) {
          setShowTimeoutWarning(true);
        }
        return next;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [operationId, operation?.status]);

  return {
    operation,
    isLoading,
    elapsedSeconds,
    showTimeoutWarning,
    isProcessing:
      operation?.status === 'pending' || operation?.status === 'processing',
  };
}
```

**Operation Status Component:**

```tsx
// frontend/src/components/common/OperationStatus.tsx
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import type { OperationStatus as StatusType } from '@/types/operation';

interface OperationStatusProps {
  status: StatusType;
  operationType: string;
  elapsedSeconds?: number;
  showTimeoutWarning?: boolean;
}

export function OperationStatus({
  status,
  operationType,
  elapsedSeconds = 0,
  showTimeoutWarning = false,
}: OperationStatusProps) {
  const renderStatusIcon = () => {
    switch (status) {
      case 'pending':
      case 'processing':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-600" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
    }
  };

  const renderStatusText = () => {
    switch (status) {
      case 'pending':
        return `${operationType}...`;
      case 'processing':
        return `${operationType}...`;
      case 'completed':
        return 'Ready!';
      case 'failed':
        return 'Failed';
    }
  };

  const statusColor = {
    pending: 'text-blue-700',
    processing: 'text-blue-700',
    completed: 'text-green-700',
    failed: 'text-red-700',
  };

  return (
    <div className="flex items-center gap-3" role="status" aria-live="polite">
      {renderStatusIcon()}
      <div>
        <p className={`font-medium ${statusColor[status]}`}>
          {renderStatusText()}
        </p>
        {(status === 'pending' || status === 'processing') &&
          elapsedSeconds > 10 && (
            <p className="text-sm text-gray-600 flex items-center gap-1 mt-1">
              <Clock className="h-3 w-3" />
              {elapsedSeconds} seconds
            </p>
          )}
        {showTimeoutWarning && (
          <p className="text-sm text-orange-600 mt-1">
            Taking longer than expected. Please wait...
          </p>
        )}
      </div>
    </div>
  );
}
```

**Processing Indicator Component:**

```tsx
// frontend/src/components/common/ProcessingIndicator.tsx
import { Loader2 } from 'lucide-react';

interface ProcessingIndicatorProps {
  message: string;
  subMessage?: string;
}

export function ProcessingIndicator({
  message,
  subMessage,
}: ProcessingIndicatorProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="h-12 w-12 animate-spin text-purple-600 mb-4" />
      <p className="text-lg font-medium text-gray-900 mb-2">{message}</p>
      {subMessage && <p className="text-sm text-gray-600">{subMessage}</p>}
    </div>
  );
}
```

**Status Badge Component:**

```tsx
// frontend/src/components/common/StatusBadge.tsx
import type { OperationStatus } from '@/types/operation';

interface StatusBadgeProps {
  status: OperationStatus;
  size?: 'sm' | 'md' | 'lg';
}

export function StatusBadge({ status, size = 'md' }: StatusBadgeProps) {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5',
  };

  const statusStyles = {
    pending: 'bg-blue-100 text-blue-800 border-blue-200',
    processing: 'bg-blue-100 text-blue-800 border-blue-200',
    completed: 'bg-green-100 text-green-800 border-green-200',
    failed: 'bg-red-100 text-red-800 border-red-200',
  };

  const statusText = {
    pending: 'Queued',
    processing: 'Processing',
    completed: 'Completed',
    failed: 'Failed',
  };

  return (
    <span
      className={`inline-flex items-center font-medium border rounded-full ${sizeClasses[size]} ${statusStyles[status]}`}
      role="status"
    >
      {statusText[status]}
    </span>
  );
}
```

**Integration Example:**

```tsx
// frontend/src/features/sessions/components/SessionDetail.tsx (excerpt)
import { useOperationPolling } from '../hooks/useOperationPolling';
import { OperationStatus } from '@/components/common/OperationStatus';
import { ProcessingIndicator } from '@/components/common/ProcessingIndicator';

function SessionDetail({ sessionId }: { sessionId: string }) {
  const { data: session } = useQuery(['session', sessionId]);
  const { operation, elapsedSeconds, showTimeoutWarning, isProcessing } =
    useOperationPolling(session?.current_operation_id);

  if (isProcessing) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <ProcessingIndicator
          message="Generating your interview question"
          subMessage="This usually takes 5-10 seconds"
        />
        <div className="mt-6 flex justify-center">
          <OperationStatus
            status={operation.status}
            operationType="Generating question"
            elapsedSeconds={elapsedSeconds}
            showTimeoutWarning={showTimeoutWarning}
          />
        </div>
      </div>
    );
  }

  // ... rest of component ...
}
```

### Testing Requirements

**Test Coverage:**

- Polling hook starts and stops correctly
- Elapsed time tracking works
- Timeout warning appears after 30 seconds
- Status indicators update in real-time
- Cleanup on component unmount

**Test Files:**

- `frontend/src/features/sessions/hooks/useOperationPolling.test.ts`
- `frontend/src/components/common/OperationStatus.test.tsx`
- `frontend/src/components/common/ProcessingIndicator.test.tsx`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.3]
- [Source: _bmad-output/project-context.md#Long-Running-Operations]
- [FR58: Display processing status during question generation]
- [FR60: Display processing status during answer analysis]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with comprehensive status transparency system
- Real-time polling with TanStack Query
- Visual indicators for all operation states
- Timeout handling and warnings
- Ready for dev implementation
