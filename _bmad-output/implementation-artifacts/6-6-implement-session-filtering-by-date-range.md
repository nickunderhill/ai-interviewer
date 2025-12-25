# Story 6.6: Implement Session Filtering by Date Range

Status: done

## Story

As a user, I want to filter my session history by date range, so that I can
focus on recent or specific time periods.

## Acceptance Criteria

1. **Given** I'm viewing session history **When** I select a date range filter
   (e.g., last 7 days, last 30 days, custom range) **Then** the frontend
   re-fetches sessions with query parameters for date filtering **And** the
   backend filters sessions where created_at is within the specified range
   **And** the filtered results display correctly **And** the filter state
   persists during the session **And** a "clear filter" option resets to show
   all sessions ✅ **IMPLEMENTED**

## Tasks / Subtasks

- [x] Task 1: Design date range filter UI (AC: #1)

  - [x] Decide filter placement: above session list (recommended)
  - [x] Design filter options:
    - Preset ranges: "Last 7 days", "Last 30 days", "Last 3 months"
    - Custom range: Date picker for start/end dates
  - [x] Add "Clear filter" button to reset

- [x] Task 2: Update backend API to support date filtering (AC: #1)

  - [x] Modify GET `/api/v1/sessions` endpoint
  - [x] Add optional query parameters:
    - `start_date` (ISO 8601 format)
    - `end_date` (ISO 8601 format)
  - [x] Filter sessions where `created_at >= start_date` AND
        `created_at <= end_date`
  - [x] Handle edge cases (invalid dates, start > end) - returns 400
  - [x] Return filtered results
  - [x] Added status validation - returns 400 for invalid status

- [x] Task 3: Create DateRangeFilter React component (AC: #1)

  - [x] Create `frontend/src/features/sessions/components/DateRangeFilter.tsx`
  - [x] Implement preset range buttons (Last 7/30/90 days) with highlighting
  - [x] Implement custom date range picker (HTML5 date inputs)
  - [x] Emit filter change events (callback to parent)

- [x] Task 4: Integrate filter with session history page (AC: #1)

  - [x] Add DateRangeFilter component to SessionHistory page
  - [x] Handle filter change events with preset logic
  - [x] Update API call with `start_date` and `end_date` query parameters
  - [x] Re-fetch sessions when filter changes (React Query)
  - [x] Display loading state during re-fetch (skeleton)

- [x] Task 5: Persist filter state during session (AC: #1)

  - [x] Store filter state in URL query params (useSearchParams)
  - [x] Shareable URLs with filters
  - [x] Restore filter state on page load/navigation

- [x] Task 6: Implement "Clear filter" functionality (AC: #1)

  - [x] Add "Clear" button
  - [x] On click, remove date filters
  - [x] Re-fetch all sessions (no date parameters)
  - [x] Reset filter UI to default state

- [x] Task 7: Add visual indicators for active filters (AC: #1)

  - [x] Highlight active preset button (indigo background)
  - [x] Display count of filtered results ("Showing N sessions in date range")
  - [x] Clear button shows when filters active

## Dev Notes

### Critical Architecture Requirements

- **Frontend Framework:** React with TypeScript.
- **Routing:** React Router v6 with URL query parameters (optional but
  recommended).
- **Date Handling:** Use `date-fns` or native Date objects for date
  manipulation.
- **API Parameters:** ISO 8601 date format (YYYY-MM-DD).
- **Backend:** FastAPI with query parameters in endpoint.
- **Validation:** Validate dates on both frontend and backend.

### Technical Implementation Details

**Suggested component structure:**

```
frontend/src/
├── pages/
│   └── SessionHistory.tsx          # Updated to include filter
├── components/
│   ├── DateRangeFilter.tsx         # NEW: Date range filter component
│   ├── SessionHistoryList.tsx      # Existing list component
│   └── SessionHistoryItem.tsx      # Existing item component
├── services/
│   └── sessionService.ts           # Updated to accept date params
└── types/
    └── session.ts                  # Session interfaces
```

**Backend API update:**

```python
# backend/app/api/v1/sessions.py

from datetime import datetime, date
from typing import Optional

@router.get("/", response_model=List[InterviewSessionResponse])
async def get_sessions(
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(InterviewSession).where(InterviewSession.user_id == current_user.id)

    if status:
        query = query.where(InterviewSession.status == status)

    if start_date:
        # Convert date to datetime at start of day
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.where(InterviewSession.created_at >= start_datetime)

    if end_date:
        # Convert date to datetime at end of day
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.where(InterviewSession.created_at <= end_datetime)

    # Validate: start_date must be before end_date
    if start_date and end_date and start_date > end_date:
        raise HTTPException(400, "start_date must be before or equal to end_date")

    query = query.order_by(InterviewSession.created_at.desc())
    result = await db.execute(query)
    sessions = result.scalars().all()
    return sessions
```

**Frontend DateRangeFilter component:**

```typescript
// DateRangeFilter.tsx
import React, { useState } from 'react';
import { subDays, format } from 'date-fns';

interface Props {
  onFilterChange: (startDate: Date | null, endDate: Date | null) => void;
}

const DateRangeFilter: React.FC<Props> = ({ onFilterChange }) => {
  const [selectedRange, setSelectedRange] = useState<string>('all');

  const handlePresetRange = (range: string) => {
    setSelectedRange(range);
    const today = new Date();

    switch (range) {
      case '7days':
        onFilterChange(subDays(today, 7), today);
        break;
      case '30days':
        onFilterChange(subDays(today, 30), today);
        break;
      case '3months':
        onFilterChange(subDays(today, 90), today);
        break;
      case 'all':
      default:
        onFilterChange(null, null);
        break;
    }
  };

  return (
    <div className="flex gap-2 mb-4">
      <button
        onClick={() => handlePresetRange('7days')}
        className={`px-4 py-2 rounded ${
          selectedRange === '7days' ? 'bg-blue-600 text-white' : 'bg-gray-200'
        }`}
      >
        Last 7 days
      </button>
      <button
        onClick={() => handlePresetRange('30days')}
        className={`px-4 py-2 rounded ${
          selectedRange === '30days' ? 'bg-blue-600 text-white' : 'bg-gray-200'
        }`}
      >
        Last 30 days
      </button>
      <button
        onClick={() => handlePresetRange('3months')}
        className={`px-4 py-2 rounded ${
          selectedRange === '3months' ? 'bg-blue-600 text-white' : 'bg-gray-200'
        }`}
      >
        Last 3 months
      </button>
      <button
        onClick={() => handlePresetRange('all')}
        className={`px-4 py-2 rounded ${
          selectedRange === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200'
        }`}
      >
        All time
      </button>
      {/* TODO: Add custom date range picker */}
    </div>
  );
};

export default DateRangeFilter;
```

**Frontend API call with date parameters:**

```typescript
// sessionService.ts
export const getSessionsByDateRange = async (
  status?: string,
  startDate?: Date | null,
  endDate?: Date | null
) => {
  const params = new URLSearchParams();

  if (status) params.append('status', status);
  if (startDate) params.append('start_date', format(startDate, 'yyyy-MM-dd'));
  if (endDate) params.append('end_date', format(endDate, 'yyyy-MM-dd'));

  const response = await axios.get(`/api/v1/sessions?${params.toString()}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  });
  return response.data;
};
```

**URL query parameters (optional, for shareable URLs):**

```typescript
// SessionHistory.tsx
import { useSearchParams } from 'react-router-dom';

const [searchParams, setSearchParams] = useSearchParams();

const handleFilterChange = (startDate: Date | null, endDate: Date | null) => {
  const params = new URLSearchParams(searchParams);

  if (startDate) {
    params.set('start_date', format(startDate, 'yyyy-MM-dd'));
  } else {
    params.delete('start_date');
  }

  if (endDate) {
    params.set('end_date', format(endDate, 'yyyy-MM-dd'));
  } else {
    params.delete('end_date');
  }

  setSearchParams(params);
  // Then fetch sessions based on params
};
```

**Visual design suggestions:**

- **Filter Buttons:** Horizontal row of preset range buttons, active button
  highlighted
- **Custom Date Picker:** Optional, collapsible or in modal
- **Active Filter Indicator:** Show selected range below buttons (e.g., "Showing
  sessions from Dec 1 - Dec 25")
- **Clear Button:** "Show all" or "Clear filter" to reset

### Related Stories

- **Story 6.1:** Session history list (extended with filtering)
- **Story 6.7:** Job posting filtering (complementary filtering feature)

### Testing Checklist

- [ ] Date range filter UI displays correctly
- [ ] Preset ranges (7 days, 30 days, etc.) filter sessions correctly
- [ ] Custom date range filters sessions correctly
- [ ] Backend validates dates and returns filtered results
- [ ] Invalid date ranges (start > end) are handled gracefully
- [ ] Filter state persists during session (URL or component state)
- [ ] "Clear filter" resets to show all sessions
- [ ] Active filter is visually indicated
- [ ] Page handles API errors gracefully
- [ ] Filter is responsive on mobile and desktop

### Definition of Done

- [ ] Backend endpoint updated to support date filtering
- [ ] DateRangeFilter component implemented
- [ ] Preset date ranges functional
- [ ] Custom date picker implemented (optional for MVP)
- [ ] Filter integrated with session history page
- [ ] Filter state persistence implemented
- [ ] Clear filter functionality implemented
- [ ] Visual indicators for active filters
- [ ] Manual testing completed
- [ ] Code reviewed and merged
