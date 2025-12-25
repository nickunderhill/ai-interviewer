# Story 6.4: Implement Score Comparison Across Sessions

Status: ready-for-dev

## Story

As a user, I want to compare scores from different interview sessions, so that I
can see if I'm improving over time.

## Acceptance Criteria

1. **Given** I have multiple completed sessions with feedback **When** I view
   the comparison feature **Then** the frontend fetches feedback for all my
   sessions **And** displays overall scores in a list or table with session
   dates **And** sorts by date to show chronological progression **And**
   highlights improvements (score increases) and regressions (score decreases)
   **And** if fewer than 2 sessions have feedback, displays a message
   encouraging more practice

## Tasks / Subtasks

- [ ] Task 1: Determine data fetching approach (AC: #1)

  - [ ] Option A: Fetch all sessions, then fetch feedback for each
    - GET `/api/v1/sessions?status=completed`
    - GET `/api/v1/sessions/{id}/feedback` for each session
  - [ ] Option B: Create new backend endpoint returning sessions with feedback
    - GET `/api/v1/sessions/with-feedback` or similar
    - Backend joins sessions and feedback tables
  - [ ] Choose approach based on performance and complexity

- [ ] Task 2: Create ScoreComparison React component (AC: #1)

  - [ ] Create `frontend/src/pages/ScoreComparison.tsx` or
        `frontend/src/components/ScoreComparison.tsx`
  - [ ] Fetch sessions with feedback
  - [ ] Handle loading and error states
  - [ ] Sort sessions by `created_at` ASC for chronological order

- [ ] Task 3: Display scores in list or table format (AC: #1)

  - [ ] Create table with columns:
    - Date (formatted, e.g., "Dec 20, 2025")
    - Job Posting (title + company)
    - Overall Score (0-100)
    - Change (score delta from previous session)
  - [ ] Alternatively, use card-based layout for mobile-friendliness
  - [ ] Show sessions in chronological order

- [ ] Task 4: Calculate and display score changes (AC: #1)

  - [ ] Calculate score delta between consecutive sessions
  - [ ] Display as "+5", "-3", or "N/A" for first session
  - [ ] Highlight improvements in green (positive delta)
  - [ ] Highlight regressions in red (negative delta)
  - [ ] Use icons (↑ for increase, ↓ for decrease) for visual clarity

- [ ] Task 5: Implement insufficient data message (AC: #1)

  - [ ] Check if fewer than 2 sessions have feedback
  - [ ] Display message: "Complete more interviews with feedback to see your
        progress comparison"
  - [ ] Include call-to-action: "Start Interview" or "Generate Feedback"
  - [ ] Show message instead of empty table

- [ ] Task 6: Add navigation to comparison view (AC: #1)

  - [ ] Decide placement: separate page or section on dashboard
  - [ ] If separate page, add route (e.g., `/comparison` or `/progress`)
  - [ ] Add navigation link in menu or dashboard
  - [ ] Ensure authentication guard is applied

## Dev Notes

### Critical Architecture Requirements

- **Frontend Framework:** React with TypeScript.
- **Routing:** React Router v6 (if separate page).
- **State Management:** React hooks or React Query for data fetching.
- **API Communication:** Axios or Fetch API with JWT authentication.
- **Styling:** Tailwind CSS (per project setup).
- **Data Sorting:** Sort by `created_at` ASC for chronological order.
- **Performance:** Consider backend aggregation if fetching many sessions.

### Technical Implementation Details

**Suggested component structure:**

```
frontend/src/
├── pages/
│   └── ScoreComparison.tsx         # Score comparison page (or component)
├── components/
│   ├── ScoreComparisonTable.tsx    # Table displaying scores
│   ├── ScoreComparisonRow.tsx      # Individual row in table
│   └── InsufficientDataMessage.tsx # Message when <2 sessions
├── services/
│   ├── sessionService.ts           # Session API calls
│   └── feedbackService.ts          # Feedback API calls
└── types/
    ├── session.ts                  # Session interface
    └── feedback.ts                 # Feedback interface
```

**Data structure for display:**

```typescript
interface SessionWithScore {
  sessionId: string;
  date: Date;
  jobTitle: string;
  company: string;
  overallScore: number;
  scoreDelta?: number; // Undefined for first session
}
```

**Backend endpoint (optional, for efficiency):**

Create GET `/api/v1/sessions/with-feedback`:

```python
# backend/app/api/v1/sessions.py

@router.get("/with-feedback", response_model=List[SessionWithFeedback])
async def get_sessions_with_feedback(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(InterviewSession, InterviewFeedback, JobPosting)
        .join(InterviewFeedback, InterviewSession.id == InterviewFeedback.session_id)
        .join(JobPosting, InterviewSession.job_posting_id == JobPosting.id)
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
        .order_by(InterviewSession.created_at.asc())
    )
    result = await db.execute(query)
    sessions = []
    for session, feedback, job_posting in result:
        sessions.append({
            "session_id": session.id,
            "created_at": session.created_at,
            "job_posting": {
                "title": job_posting.title,
                "company": job_posting.company
            },
            "overall_score": feedback.overall_score
        })
    return sessions
```

**Frontend calculation:**

```typescript
// Calculate score deltas
const sessionsWithDeltas = sessionsWithScores.map((session, index) => {
  if (index === 0) {
    return { ...session, scoreDelta: undefined };
  }
  const previousScore = sessionsWithScores[index - 1].overallScore;
  return { ...session, scoreDelta: session.overallScore - previousScore };
});
```

**Visual design suggestions:**

- **Table Layout:**
  - Columns: Date | Job Posting | Overall Score | Change
  - Responsive: Stack columns on mobile
  - Alternating row colors for readability
- **Score Delta Display:**
  - Green text and ↑ icon for positive change (e.g., "+5 ↑")
  - Red text and ↓ icon for negative change (e.g., "-3 ↓")
  - Gray text for first session or no change ("N/A" or "—")
- **Insufficient Data Message:**
  - Centered card with icon
  - Message: "You need at least 2 completed interviews with feedback to compare
    scores."
  - Button: "View Your Interviews"

### Related Stories

- **Story 6.1:** Session history (data source)
- **Story 5.5:** Feedback retrieval (data source)
- **Story 6.3:** Performance metrics dashboard (similar data usage)
- **Story 6.5:** Score trends visualization (complementary view)

### Testing Checklist

- [ ] Comparison displays correct scores for all sessions with feedback
- [ ] Sessions are sorted chronologically (oldest to newest)
- [ ] Score deltas are calculated correctly
- [ ] Improvements are highlighted in green
- [ ] Regressions are highlighted in red
- [ ] First session shows "N/A" or no delta
- [ ] Insufficient data message displays when <2 sessions with feedback
- [ ] Page handles API errors gracefully
- [ ] Authentication is enforced
- [ ] Page is responsive on mobile and desktop

### Definition of Done

- [ ] Backend endpoint created (if chosen)
- [ ] Frontend component implemented
- [ ] Scores displayed in chronological order
- [ ] Score deltas calculated and displayed
- [ ] Visual highlighting for improvements/regressions
- [ ] Insufficient data message implemented
- [ ] Navigation added (if separate page)
- [ ] Component is responsive
- [ ] Manual testing completed
- [ ] Code reviewed and merged
