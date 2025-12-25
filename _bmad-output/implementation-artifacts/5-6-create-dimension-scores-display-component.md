# Story 5.6: Create Dimension Scores Display Component

Status: ready-for-dev

## Story

As a user, I want to see visual indicators for each feedback dimension, so that
I can quickly understand my performance breakdown.

## Acceptance Criteria

1. **Given** I'm viewing feedback **When** the frontend receives dimension
   scores **Then** it displays 4 separate scores: Technical Accuracy,
   Communication Clarity, Problem-Solving Approach, Relevance to Job **And**
   each score is shown with a progress bar or visual indicator (0-100) **And**
   the overall score is prominently displayed **And** color coding indicates
   performance level (e.g., red <60, yellow 60-79, green ≥80) **And** the UI is
   responsive and clear

## Tasks / Subtasks

- [ ] Task 1: Define feedback score types (AC: #1)

  - [ ] Create `frontend/src/features/feedback/types/feedback.ts`
  - [ ] Define `FeedbackScores` type with the 4 dimension scores + overall_score

- [ ] Task 2: Implement component (AC: #1)

  - [ ] Create `frontend/src/features/feedback/components/DimensionScores.tsx`
  - [ ] Props:
    - [ ] dimension scores (0..100)
    - [ ] overall score (0..100)
  - [ ] Display:
    - [ ] prominent overall score
    - [ ] four labeled rows/cards
    - [ ] progress bar per dimension
  - [ ] Apply color coding using Tailwind utility classes (no custom colors)
  - [ ] Ensure keyboard and screen-reader friendly markup

- [ ] Task 3: Add tests (AC: #1)

  - [ ] Create
        `frontend/src/features/feedback/components/__tests__/DimensionScores.test.tsx`
  - [ ] Test labels render
  - [ ] Test score text renders (e.g., "82/100")
  - [ ] Test color class mapping for <60, 60-79, ≥80

## Dev Notes

### Critical Architecture Requirements

- React 18 functional components.
- Feature-based organization: `src/features/feedback/...`.
- Accessibility: semantic HTML and visible focus indicators.

### Color Mapping

- `< 60` → red
- `60..79` → yellow
- `>= 80` → green

Use Tailwind classes like `bg-red-500`, `bg-yellow-500`, `bg-green-500` (or the
closest existing palette already in use in the app).

### Technical Implementation Details

**Suggested files:**

```
frontend/src/features/feedback/types/feedback.ts
frontend/src/features/feedback/components/DimensionScores.tsx
frontend/src/features/feedback/components/__tests__/DimensionScores.test.tsx
```

**Component sketch:**

```tsx
export type DimensionKey =
  | 'technicalAccuracy'
  | 'communicationClarity'
  | 'problemSolving'
  | 'relevance';

type Props = {
  overallScore: number;
  technicalAccuracy: number;
  communicationClarity: number;
  problemSolving: number;
  relevance: number;
};

export default function DimensionScores(props: Props) {
  // map score→color class
  // render progress bars
}
```

### References

- Frontend conventions: `_bmad-output/project-context.md#Frontend Patterns`
- Existing test patterns: `frontend/src/features/auth/components/__tests__/*`

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

- Responsive layout with 4 progress bars
- Correct color thresholds
- Tests cover rendering and class mapping

### File List

_To be filled by dev agent_
