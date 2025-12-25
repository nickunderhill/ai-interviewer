# Story 6.3: Create Performance Metrics Dashboard

Status: ready-for-dev

## Story

As a user, I want to see aggregate statistics about my interviews, so that I can
track my overall progress.

## Acceptance Criteria

1. **Given** I am authenticated with completed sessions **When** I navigate to
   the dashboard **Then** the system calculates and displays: total number of
   completed interviews, average overall score (across all sessions with
   feedback), total questions answered (sum of all current_question_numbers),
   most practiced job roles (grouped by job_posting title/company) **And**
   metrics update automatically as new sessions/feedback are added **And** if no
   data exists, displays appropriate zero-state messages

## Tasks / Subtasks

- [ ] Task 1: Design and plan metrics to display (AC: #1)

  - [ ] Confirm metrics: total completed interviews, average score, total
        questions, most practiced roles
  - [ ] Determine data sources:
    - Total completed: count sessions with `status=completed`
    - Average score: average of `overall_score` from feedback records
    - Total questions: sum of `current_question_number` from all sessions
    - Most practiced roles: group sessions by job_posting, count occurrences
  - [ ] Plan frontend data fetching strategy (multiple API calls or new
        aggregation endpoint)

- [ ] Task 2: Create metrics aggregation logic (AC: #1)

  - [ ] Option A: Frontend calculates from existing endpoints
    - Fetch GET `/api/v1/sessions` (all user's sessions)
    - Fetch GET `/api/v1/sessions/{id}/feedback` for each session with feedback
    - Calculate aggregations in frontend
  - [ ] Option B: Create new backend aggregation endpoint (recommended for
        performance)
    - Create GET `/api/v1/metrics/dashboard` endpoint
    - Aggregate data in backend using SQL queries
    - Return computed metrics in single response
  - [ ] Implement chosen approach

- [ ] Task 3: Create Dashboard React component (AC: #1)

  - [ ] Create `frontend/src/pages/Dashboard.tsx` or similar
  - [ ] Fetch aggregated metrics (from API or multiple endpoints)
  - [ ] Handle loading and error states
  - [ ] Store metrics in component state

- [ ] Task 4: Display total completed interviews (AC: #1)

  - [ ] Create metric card component showing count
  - [ ] Label: "Completed Interviews" or "Total Sessions"
  - [ ] Display number prominently
  - [ ] Add icon for visual appeal

- [ ] Task 5: Display average overall score (AC: #1)

  - [ ] Calculate average from all feedback records
  - [ ] Display as percentage or decimal (e.g., "85%" or "85/100")
  - [ ] Label: "Average Score"
  - [ ] Use color coding (green for high, yellow for medium, red for low)
  - [ ] Handle case where no feedback exists (display "N/A" or message)

- [ ] Task 6: Display total questions answered (AC: #1)

  - [ ] Sum `current_question_number` from all completed sessions
  - [ ] Display total count
  - [ ] Label: "Questions Answered" or "Total Questions"
  - [ ] Add icon for visual appeal

- [ ] Task 7: Display most practiced job roles (AC: #1)

  - [ ] Group sessions by job_posting (title + company)
  - [ ] Count sessions per job posting
  - [ ] Display top 3-5 most practiced roles
  - [ ] Show role name and count (e.g., "Senior Backend Engineer at TechCorp
        (3)")
  - [ ] Consider bar chart or list format

- [ ] Task 8: Implement zero-state messages (AC: #1)

  - [ ] If no completed sessions exist: "Start your first interview to see your
        progress"
  - [ ] If no feedback exists: "Complete feedback generation to see your average
        score"
  - [ ] Display friendly encouragement messages
  - [ ] Include call-to-action buttons (e.g., "Start Interview")

- [ ] Task 9: Ensure automatic updates (AC: #1)

  - [ ] Metrics re-fetch when user navigates to dashboard
  - [ ] Consider real-time updates or refresh button
  - [ ] Cache data appropriately to avoid excessive API calls

- [ ] Task 10: Add navigation to dashboard (AC: #1)

  - [ ] Add route to React Router (e.g., `/dashboard`)
  - [ ] Add navigation link in main menu (make it prominent, possibly home page)
  - [ ] Ensure authentication guard is applied

## Dev Notes

### Critical Architecture Requirements

- **Frontend Framework:** React with TypeScript.
- **Routing:** React Router v6.
- **State Management:** React hooks or React Query for data fetching.
- **API Communication:** Axios or Fetch API with JWT authentication.
- **Styling:** Tailwind CSS (per project setup).
- **Data Aggregation:** Consider backend endpoint for efficiency, or calculate
  in frontend if simple.
- **Performance:** Minimize API calls, use efficient queries.

### Technical Implementation Details

**Suggested component structure:**

```
frontend/src/
├── pages/
│   └── Dashboard.tsx               # Main dashboard page
├── components/
│   ├── MetricCard.tsx              # Reusable metric display card
│   ├── MostPracticedRoles.tsx      # Most practiced roles section
│   └── EmptyState.tsx              # Zero-state component
├── services/
│   ├── metricsService.ts           # API calls for metrics (if new endpoint)
│   └── sessionService.ts           # Existing session API calls
└── types/
    └── metrics.ts                  # TypeScript interfaces for metrics
```

**Backend aggregation endpoint (recommended):**

Create GET `/api/v1/metrics/dashboard`:

```python
# backend/app/api/v1/metrics.py

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Count completed sessions
    completed_count = await db.scalar(
        select(func.count(InterviewSession.id))
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
    )

    # Calculate average score
    avg_score = await db.scalar(
        select(func.avg(InterviewFeedback.overall_score))
        .join(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
    )

    # Sum total questions
    total_questions = await db.scalar(
        select(func.sum(InterviewSession.current_question_number))
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
    )

    # Most practiced roles
    roles_query = (
        select(
            JobPosting.title,
            JobPosting.company,
            func.count(InterviewSession.id).label("count")
        )
        .join(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
        .group_by(JobPosting.id, JobPosting.title, JobPosting.company)
        .order_by(func.count(InterviewSession.id).desc())
        .limit(5)
    )
    roles_result = await db.execute(roles_query)
    most_practiced = [
        {"title": r.title, "company": r.company, "count": r.count}
        for r in roles_result
    ]

    return {
        "completed_interviews": completed_count or 0,
        "average_score": round(avg_score, 1) if avg_score else None,
        "total_questions_answered": total_questions or 0,
        "most_practiced_roles": most_practiced
    }
```

**Response format:**

```json
{
  "completed_interviews": 12,
  "average_score": 78.5,
  "total_questions_answered": 96,
  "most_practiced_roles": [
    { "title": "Senior Backend Engineer", "company": "TechCorp", "count": 5 },
    { "title": "Full Stack Developer", "company": "StartupXYZ", "count": 4 },
    { "title": "DevOps Engineer", "company": "CloudCo", "count": 3 }
  ]
}
```

**Visual design suggestions:**

- **Layout:** Grid of metric cards (2x2 or 4 cards in a row on desktop)
- **Metric Cards:** Large number, label, icon, color-coded
- **Most Practiced Roles:** Separate section below cards, list or horizontal bar
  chart
- **Empty State:** Centered message with illustration, call-to-action button

**Styling:**

- Use Tailwind classes for consistent spacing and colors
- Large, bold numbers for metrics
- Icons from icon library (e.g., Heroicons, Lucide)
- Responsive grid (stacks on mobile)

### Related Stories

- **Story 6.1:** Session history (data source for metrics)
- **Story 5.5:** Feedback retrieval (data source for average score)
- **Story 6.4:** Score comparison (may share similar data)

### Testing Checklist

- [ ] Dashboard displays all metrics correctly
- [ ] Total completed interviews count is accurate
- [ ] Average score calculation is correct
- [ ] Total questions answered sum is accurate
- [ ] Most practiced roles are displayed and sorted correctly
- [ ] Zero-state messages display when no data exists
- [ ] Metrics update when navigating to dashboard after completing sessions
- [ ] Page handles API errors gracefully
- [ ] Authentication is enforced
- [ ] Page is responsive on mobile and desktop

### Definition of Done

- [ ] Backend aggregation endpoint created (if chosen)
- [ ] Frontend dashboard component implemented
- [ ] All metrics displayed correctly
- [ ] Zero-state messages implemented
- [ ] Navigation added to app menu
- [ ] Component is responsive
- [ ] Manual testing completed
- [ ] Code reviewed and merged
