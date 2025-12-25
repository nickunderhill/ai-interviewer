# Story 6.7: Implement Session Filtering by Job Posting

Status: done

## Story

As a user, I want to filter sessions by job posting, so that I can see all
interviews for a specific role.

## Acceptance Criteria

1. **Given** I'm viewing session history **When** I select a job posting filter
   (dropdown of my job postings) **Then** the frontend re-fetches sessions with
   query parameter `job_posting_id` **And** the backend filters sessions where
   job_posting_id matches **And** the filtered results display correctly **And**
   the filter state persists during the session **And** a "clear filter" option
   resets to show all sessions ✅ **IMPLEMENTED**

## Tasks / Subtasks

- [x] Task 1: Design job posting filter UI (AC: #1)

  - [x] Placement: above session list, below date range filter
  - [x] Design as dropdown/select with user's job postings
  - [x] Display format: "Job Title at Company"
  - [x] "All job postings" default option + Clear button

- [x] Task 2: Update backend API to support job posting filtering (AC: #1)

  - [x] GET `/api/v1/sessions` supports `job_posting_id` query parameter
  - [x] Filter sessions where `job_posting_id` matches the provided UUID
  - [x] Security: Verify user owns job posting (404 if not found/owned)
  - [x] Return filtered results

- [x] Task 3: Fetch user's job postings for filter dropdown (AC: #1)

  - [x] Created jobs feature module with useJobPostings hook
  - [x] Uses GET `/api/v1/job-postings` endpoint
  - [x] Display format: title + company in dropdown

- [x] Task 4: Create JobPostingFilter React component (AC: #1)

  - [x] Created `frontend/src/features/sessions/components/JobPostingFilter.tsx`
  - [x] Dropdown/select with job postings
  - [x] "All job postings" option (value: empty string)
  - [x] Emit filter change event (callback)
  - [x] Loading skeleton while fetching

- [x] Task 5: Integrate filter with session history page (AC: #1)

  - [x] Added JobPostingFilter to SessionHistory page
  - [x] Handle filter change events
  - [x] Update API call with `job_posting_id` query parameter
  - [x] Re-fetch sessions when filter changes (React Query)
  - [x] Display loading state during re-fetch

- [x] Task 6: Persist filter state during session (AC: #1)

  - [x] Store in URL query params (useSearchParams)
  - [x] Shareable URLs with filters
  - [x] Restore filter state on page load/navigation

- [x] Task 7: Implement "Clear filter" functionality (AC: #1)

  - [x] Clear button removes `job_posting_id` filter
  - [x] Re-fetch all sessions (no job_posting_id parameter)
  - [x] Reset filter UI to default state

- [x] Task 8: Add visual indicators for active filters (AC: #1)

  - [x] Show count of filtered results ("Showing N sessions for selected job
        posting")
  - [x] Display selected job posting below dropdown
  - [x] Clear button visible when filter active

- [x] Task 9: Combine with date range filter (AC: #1)

  - [x] Job posting filter works alongside date range filter
  - [x] Both filters apply simultaneously in API call
  - [x] Update API with both `job_posting_id` and date parameters
  - [x] Clear one filter doesn't affect the other

## Dev Notes

### Critical Architecture Requirements

- **Frontend Framework:** React with TypeScript.
- **Routing:** React Router v6 with URL query parameters (optional but
  recommended).
- **API Parameters:** UUID format for `job_posting_id`.
- **Backend:** FastAPI with query parameters in endpoint.
- **Validation:** Validate job_posting_id on backend (ensure user owns it).
- **Multiple Filters:** Support combining with date range filter (Story 6.6).

### Technical Implementation Details

**Suggested component structure:**

```
frontend/src/
├── pages/
│   └── SessionHistory.tsx          # Updated to include filter
├── components/
│   ├── DateRangeFilter.tsx         # Existing from Story 6.6
│   ├── JobPostingFilter.tsx        # NEW: Job posting filter component
│   ├── SessionHistoryList.tsx      # Existing list component
│   └── SessionHistoryItem.tsx      # Existing item component
├── services/
│   ├── sessionService.ts           # Updated to accept job_posting_id param
│   └── jobPostingService.ts        # Existing service for fetching job
│       postings
└── types/
    ├── session.ts                  # Session interfaces
    └── jobPosting.ts               # JobPosting interface
```

**Backend API update:**

```python
# backend/app/api/v1/sessions.py

from uuid import UUID
from typing import Optional

@router.get("/", response_model=List[InterviewSessionResponse])
async def get_sessions(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    job_posting_id: Optional[UUID] = None,  # NEW
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(InterviewSession).where(InterviewSession.user_id == current_user.id)

    if status:
        query = query.where(InterviewSession.status == status)

    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.where(InterviewSession.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.where(InterviewSession.created_at <= end_datetime)

    if job_posting_id:
        # Verify user owns the job posting (security check)
        job_posting = await db.get(JobPosting, job_posting_id)
        if not job_posting or job_posting.user_id != current_user.id:
            raise HTTPException(404, "Job posting not found")
        query = query.where(InterviewSession.job_posting_id == job_posting_id)

    query = query.order_by(InterviewSession.created_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()
    return sessions
```

**Frontend JobPostingFilter component:**

```typescript
// JobPostingFilter.tsx
import React, { useEffect, useState } from 'react';
import { getJobPostings } from '../services/jobPostingService';

interface JobPosting {
  id: string;
  title: string;
  company: string;
}

interface Props {
  onFilterChange: (jobPostingId: string | null) => void;
}

const JobPostingFilter: React.FC<Props> = ({ onFilterChange }) => {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [selectedJobPostingId, setSelectedJobPostingId] = useState<
    string | null
  >(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobPostings = async () => {
      try {
        const postings = await getJobPostings();
        setJobPostings(postings);
      } catch (error) {
        console.error('Failed to fetch job postings:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobPostings();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value === '' ? null : e.target.value;
    setSelectedJobPostingId(value);
    onFilterChange(value);
  };

  if (loading) {
    return <div>Loading job postings...</div>;
  }

  return (
    <div className="mb-4">
      <label
        htmlFor="job-posting-filter"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Filter by Job Posting
      </label>
      <select
        id="job-posting-filter"
        value={selectedJobPostingId || ''}
        onChange={handleChange}
        className="w-full md:w-64 px-4 py-2 border border-gray-300 rounded"
      >
        <option value="">All job postings</option>
        {jobPostings.map(posting => (
          <option key={posting.id} value={posting.id}>
            {posting.title} at {posting.company}
          </option>
        ))}
      </select>
    </div>
  );
};

export default JobPostingFilter;
```

**Frontend API call with job_posting_id parameter:**

```typescript
// sessionService.ts
export const getSessions = async (
  status?: string,
  startDate?: Date | null,
  endDate?: Date | null,
  jobPostingId?: string | null
) => {
  const params = new URLSearchParams();

  if (status) params.append('status', status);
  if (startDate) params.append('start_date', format(startDate, 'yyyy-MM-dd'));
  if (endDate) params.append('end_date', format(endDate, 'yyyy-MM-dd'));
  if (jobPostingId) params.append('job_posting_id', jobPostingId);

  const response = await axios.get(`/api/v1/sessions?${params.toString()}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return response.data;
};
```

**Combining filters in SessionHistory page:**

```typescript
// SessionHistory.tsx
const SessionHistory: React.FC = () => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);
  const [jobPostingId, setJobPostingId] = useState<string | null>(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const data = await getSessions(
        'completed',
        startDate,
        endDate,
        jobPostingId
      );
      setSessions(data);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [startDate, endDate, jobPostingId]);

  return (
    <div>
      <h1>Session History</h1>
      <DateRangeFilter
        onFilterChange={(start, end) => {
          setStartDate(start);
          setEndDate(end);
        }}
      />
      <JobPostingFilter onFilterChange={setJobPostingId} />
      {loading ? (
        <div>Loading...</div>
      ) : (
        <SessionHistoryList sessions={sessions} />
      )}
    </div>
  );
};
```

**URL query parameters (optional, for shareable URLs):**

```typescript
// SessionHistory.tsx
import { useSearchParams } from 'react-router-dom';

const [searchParams, setSearchParams] = useSearchParams();

const handleJobPostingFilterChange = (jobPostingId: string | null) => {
  const params = new URLSearchParams(searchParams);

  if (jobPostingId) {
    params.set('job_posting_id', jobPostingId);
  } else {
    params.delete('job_posting_id');
  }

  setSearchParams(params);
  // Then fetch sessions based on params
};
```

**Visual design suggestions:**

- **Dropdown:** Standard HTML select or custom styled dropdown (e.g., React
  Select)
- **Label:** "Filter by Job Posting" or "Job Posting"
- **Options:** "All job postings" + list of user's job postings
- **Active Filter Indicator:** Show selected job posting below dropdown or as a
  badge
- **Layout:** Place near date range filter (Story 6.6), either side-by-side or
  stacked

### Related Stories

- **Story 6.1:** Session history list (extended with filtering)
- **Story 6.6:** Date range filtering (complementary filtering feature)

### Testing Checklist

- [ ] Job posting filter UI displays correctly
- [ ] Dropdown lists all user's job postings
- [ ] Selecting a job posting filters sessions correctly
- [ ] Backend validates job_posting_id and enforces ownership
- [ ] Filter state persists during session (URL or component state)
- [ ] "All job postings" option resets filter
- [ ] Filter works alongside date range filter (both apply simultaneously)
- [ ] Active filter is visually indicated
- [ ] Page handles API errors gracefully (e.g., invalid job_posting_id)
- [ ] Filter is responsive on mobile and desktop

### Definition of Done

- [ ] Backend endpoint updated to support job posting filtering
- [ ] JobPostingFilter component implemented
- [ ] Dropdown lists user's job postings
- [ ] Filter integrated with session history page
- [ ] Filter state persistence implemented
- [ ] Clear filter functionality implemented
- [ ] Filter combines with date range filter
- [ ] Visual indicators for active filters
- [ ] Manual testing completed
- [ ] Code reviewed and merged
