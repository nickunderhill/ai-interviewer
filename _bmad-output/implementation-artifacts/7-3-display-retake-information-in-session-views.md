# Story 7.3: Display Retake Information in Session Views

Status: ready-for-dev

## Story

As a user, I want to see retake numbers in my session history, so that I can
identify which attempt each session represents.

## Acceptance Criteria

1. **Given** I'm viewing sessions **When** a session is a retake
   (retake_number > 1) **Then** the UI displays a badge or label indicating
   "Attempt #X" or "Retake #X" **And** the original session and all its retakes
   are visually linked (e.g., grouped or indicated with icons) **And** first
   attempts (retake_number = 1) are clearly distinguished from retakes **And**
   the display is consistent across session list and detail views ✅

## Tasks / Subtasks

- [ ] Task 1: Update SessionResponse schema to include retake fields (AC: #1)

  - [ ] Verify retake_number and original_session_id in API response
  - [ ] Update TypeScript interfaces to match backend schema
  - [ ] Add fields to session type definitions

- [ ] Task 2: Create RetakeBadge component (AC: #1)

  - [ ] Create `frontend/src/features/sessions/components/RetakeBadge.tsx`
  - [ ] Display "Attempt #N" badge for all sessions
  - [ ] Visual distinction: different colors for first attempt vs retakes
  - [ ] Props: retakeNumber, isOriginal (computed from retake_number === 1)
  - [ ] Use Tailwind CSS for styling
  - [ ] Accessibility: proper ARIA labels

- [ ] Task 3: Add retake indicator to SessionCard component (AC: #1)

  - [ ] Import and use RetakeBadge in SessionCard
  - [ ] Position badge prominently (top-right or next to session title)
  - [ ] Show for all sessions in list view
  - [ ] Ensure responsive design

- [ ] Task 4: Add retake information to SessionDetail view (AC: #1)

  - [ ] Display RetakeBadge in session header
  - [ ] Show attempt number prominently
  - [ ] Add context: "This is your [1st/2nd/3rd] attempt at this role"
  - [ ] Consistent styling with list view

- [ ] Task 5: Implement visual linking of retake chains (AC: #1)

  - [ ] Add "View all attempts" link in session detail
  - [ ] Link to filtered view showing all sessions with same original_session_id
  - [ ] Display retake chain breadcrumb (Attempt 1 → Attempt 2 → Attempt 3)
  - [ ] Highlight current session in chain

- [ ] Task 6: Add retake action button for completed sessions (AC: #1)

  - [ ] Show "Retake Interview" button on completed sessions
  - [ ] Call POST /api/v1/sessions/{id}/retake endpoint (from Story 7.2)
  - [ ] Handle success: redirect to new session or show success message
  - [ ] Handle errors: display user-friendly error messages
  - [ ] Disable if session is not completed

- [ ] Task 7: Update session filtering to support retake chains (AC: #1)

  - [ ] Add option to "Group by retake chain" in filters
  - [ ] When grouped, show sessions hierarchically
  - [ ] Show count of attempts per job posting

- [ ] Task 8: Add retake information to session history page (AC: #1)
  - [ ] Update SessionHistory component to display retake badges
  - [ ] Sort options: include "Group by attempt" option
  - [ ] Show retake count per job posting in summary

## Dev Notes

### Critical Architecture Requirements

**Frontend:**

- **Framework:** React 18+ with TypeScript (strict mode)
- **Styling:** Tailwind CSS v3+
- **State Management:** TanStack Query v5 for server state
- **Routing:** React Router v6
- **HTTP:** Axios with interceptors
- **Component Location:** `frontend/src/features/sessions/components/`

**Design Patterns:**

- Functional components with hooks only
- TypeScript interfaces for all props
- Reusable badge component
- Consistent styling across views
- Responsive design (mobile-first)

### Component Implementation Patterns

**RetakeBadge Component:**

```tsx
// frontend/src/features/sessions/components/RetakeBadge.tsx
interface RetakeBadgeProps {
  retakeNumber: number;
  className?: string;
}

export function RetakeBadge({
  retakeNumber,
  className = '',
}: RetakeBadgeProps) {
  const isOriginal = retakeNumber === 1;

  const badgeClasses = isOriginal
    ? 'bg-blue-100 text-blue-800 border-blue-300'
    : 'bg-purple-100 text-purple-800 border-purple-300';

  const label = isOriginal ? 'Original Attempt' : `Attempt #${retakeNumber}`;

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClasses} ${className}`}
      aria-label={`This is ${label.toLowerCase()}`}
    >
      {label}
    </span>
  );
}
```

**SessionCard with Retake Badge:**

```tsx
// frontend/src/features/sessions/components/SessionCard.tsx
import { RetakeBadge } from './RetakeBadge';

interface SessionCardProps {
  session: Session;
  onClick?: () => void;
}

export function SessionCard({ session, onClick }: SessionCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold">{session.job_posting?.title}</h3>
        <RetakeBadge retakeNumber={session.retake_number} />
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        <p>
          Status: <span className="capitalize">{session.status}</span>
        </p>
        <p>Created: {formatDate(session.created_at)}</p>
        {session.retake_number > 1 && (
          <p className="text-purple-600 font-medium">
            <Link to={`/sessions?original=${session.original_session_id}`}>
              View all attempts →
            </Link>
          </p>
        )}
      </div>

      {session.status === 'completed' && (
        <RetakeButton sessionId={session.id} className="mt-4" />
      )}
    </div>
  );
}
```

**RetakeButton Component:**

```tsx
// frontend/src/features/sessions/components/RetakeButton.tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { retakeInterview } from '../api/sessions';

interface RetakeButtonProps {
  sessionId: string;
  className?: string;
}

export function RetakeButton({ sessionId, className = '' }: RetakeButtonProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const retakeMutation = useMutation({
    mutationFn: () => retakeInterview(sessionId),
    onSuccess: newSession => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      navigate(`/sessions/${newSession.id}`);
    },
    onError: (error: any) => {
      // Handle error with toast/notification
      console.error('Failed to create retake:', error);
    },
  });

  return (
    <button
      onClick={e => {
        e.stopPropagation(); // Prevent card click
        retakeMutation.mutate();
      }}
      disabled={retakeMutation.isPending}
      className={`px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 ${className}`}
    >
      {retakeMutation.isPending ? 'Creating...' : 'Retake Interview'}
    </button>
  );
}
```

**API Integration:**

```typescript
// frontend/src/features/sessions/api/sessions.ts
import axios from 'axios';
import type { Session } from '../types';

export async function retakeInterview(sessionId: string): Promise<Session> {
  const response = await axios.post<Session>(
    `/api/v1/sessions/${sessionId}/retake`
  );
  return response.data;
}

export async function getSessionsByOriginal(
  originalSessionId: string
): Promise<Session[]> {
  const response = await axios.get<{ items: Session[] }>(
    `/api/v1/sessions?original_session_id=${originalSessionId}`
  );
  return response.data.items;
}
```

**TypeScript Type Updates:**

```typescript
// frontend/src/features/sessions/types/index.ts
export interface Session {
  id: string;
  user_id: string;
  job_posting_id: string | null;
  status: 'active' | 'completed';
  current_question_number: number;
  retake_number: number; // ADD THIS
  original_session_id: string | null; // ADD THIS
  created_at: string;
  updated_at: string;
  job_posting?: JobPosting;
  messages?: Message[];
  feedback?: Feedback;
}
```

### Visual Design Guidelines

**Badge Styling:**

- Original attempts: Blue badge (calm, professional)
- Retakes: Purple badge (indicates progression, improvement)
- Size: Small, unobtrusive (text-xs)
- Position: Top-right of card or next to title
- Responsive: Maintain visibility on mobile

**Retake Chain Display:**

- Use breadcrumb-style navigation
- Show progress: Attempt 1 → Attempt 2 → Attempt 3
- Highlight current session
- Link to each attempt in chain

**Accessibility:**

- ARIA labels on badges
- Screen reader friendly descriptions
- Keyboard navigation support
- Color contrast compliance (WCAG AA)

### Testing Checklist

**Component Tests:**

- [ ] RetakeBadge renders correctly for retake_number=1
- [ ] RetakeBadge renders correctly for retake_number>1
- [ ] RetakeBadge applies correct styling for each type
- [ ] SessionCard displays retake badge
- [ ] RetakeButton calls API correctly
- [ ] RetakeButton handles errors gracefully

**Integration Tests:**

- [ ] Retake badge appears in session list
- [ ] Retake badge appears in session detail
- [ ] Clicking retake button creates new session
- [ ] Navigation to new session after retake
- [ ] View all attempts link filters correctly

**Visual Tests:**

- [ ] Badge placement consistent across views
- [ ] Responsive design on mobile/tablet/desktop
- [ ] Color scheme matches design system
- [ ] Hover states work correctly

### Project Structure References

**Files to Create:**

- `frontend/src/features/sessions/components/RetakeBadge.tsx`
- `frontend/src/features/sessions/components/RetakeButton.tsx`

**Files to Modify:**

- `frontend/src/features/sessions/components/SessionCard.tsx`
- `frontend/src/features/sessions/components/SessionDetail.tsx`
- `frontend/src/features/sessions/types/index.ts`
- `frontend/src/features/sessions/api/sessions.ts`

**Dependencies:**

- Story 7.1: Database fields exist
- Story 7.2: Retake endpoint available
- Existing: SessionCard, SessionDetail components

### Related Context

**From Project Context
([project-context.md](../_bmad-output/project-context.md)):**

- React 18+ functional components only
- Tailwind CSS v3+ for styling
- TanStack Query for server state
- TypeScript strict mode
- Axios for HTTP client

**From Architecture ([architecture.md](../_bmad-output/architecture.md)):**

- Frontend: React SPA with component-based architecture
- State management: TanStack Query for server state
- Routing: React Router v6
- Design: Responsive, mobile-first

**From Epic 7 ([epics.md](../_bmad-output/epics.md)):**

- Story 7.3 enables visual identification of retakes
- Foundation for stories 7.4-7.5 (score comparison)
- User-facing feature for improvement tracking

**From Recent Stories (Epic 6):**

- SessionCard component exists in session history
- SessionDetail component exists for session view
- Filtering patterns established in Stories 6.6-6.7

### Anti-Patterns to Avoid

❌ Don't hardcode badge text - use computed values from retake_number  
❌ Don't make badges too large - should be subtle indicators  
❌ Don't forget mobile responsiveness  
❌ Don't show retake button on active sessions  
❌ Don't forget error handling for retake API call  
❌ Don't use different styling patterns across list/detail views

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent_
