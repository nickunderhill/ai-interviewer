# Story 6.5: Create Score Trends Visualization

Status: ready-for-dev

## Story

As a user, I want to see a visual chart of my score trends, so that I can easily
understand my improvement trajectory.

## Acceptance Criteria

1. **Given** I have completed sessions with feedback **When** I view the trends
   chart **Then** the frontend renders a line or bar chart with x-axis as
   session dates and y-axis as overall scores (0-100) **And** the chart clearly
   shows the trend direction (improving, stable, declining) **And** uses a
   responsive charting library (e.g., Recharts, Chart.js) **And** includes
   tooltips showing session details on hover **And** if data is insufficient (<2
   feedback records), displays a message instead of an empty chart

## Tasks / Subtasks

- [ ] Task 1: Choose and install charting library (AC: #1)

  - [ ] Evaluate options:
    - **Recharts:** React-friendly, declarative, responsive
    - **Chart.js with react-chartjs-2:** Powerful, widely used
    - **Victory:** Flexible, React-native compatible
    - **Nivo:** Beautiful, D3-based
  - [ ] Install chosen library (e.g., `npm install recharts`)
  - [ ] Add TypeScript types if needed (e.g., `@types/recharts`)

- [ ] Task 2: Fetch sessions with feedback (AC: #1)

  - [ ] Reuse data fetching from Story 6.4 (sessions with feedback)
  - [ ] Option A: GET `/api/v1/sessions/with-feedback`
  - [ ] Option B: Fetch sessions + feedback separately
  - [ ] Sort by `created_at` ASC for chronological order

- [ ] Task 3: Create ScoreTrendsChart React component (AC: #1)

  - [ ] Create `frontend/src/components/ScoreTrendsChart.tsx`
  - [ ] Accept sessions data as props
  - [ ] Transform data into chart-compatible format:
    - x-axis: session date (formatted)
    - y-axis: overall_score (0-100)

- [ ] Task 4: Implement line or bar chart (AC: #1)

  - [ ] Use chosen library to render chart
  - [ ] Configure x-axis: dates (formatted, e.g., "Dec 20")
  - [ ] Configure y-axis: scores (0-100 range)
  - [ ] Use line chart for trend visualization (recommended)
  - [ ] Alternatively, use bar chart if preferred
  - [ ] Ensure chart is responsive (adjusts to container width)

- [ ] Task 5: Add tooltips with session details (AC: #1)

  - [ ] Configure tooltip to display on hover
  - [ ] Tooltip content:
    - Date (full format, e.g., "December 20, 2025")
    - Job posting (title + company)
    - Overall score (e.g., "Score: 85/100")
  - [ ] Style tooltip for readability

- [ ] Task 6: Visualize trend direction (AC: #1)

  - [ ] Use color coding for line:
    - Green: improving trend (overall increase)
    - Red: declining trend (overall decrease)
    - Blue/Gray: stable trend
  - [ ] Alternatively, add trend line (linear regression) overlay
  - [ ] Consider adding labels or annotations for significant changes

- [ ] Task 7: Implement insufficient data message (AC: #1)

  - [ ] Check if fewer than 2 feedback records exist
  - [ ] Display message instead of chart:
    - "You need at least 2 completed interviews with feedback to see your score
      trends."
  - [ ] Include call-to-action: "Complete more interviews"
  - [ ] Show placeholder or illustration

- [ ] Task 8: Integrate chart into appropriate page (AC: #1)

  - [ ] Add chart to dashboard (Story 6.3) or score comparison page (Story 6.4)
  - [ ] Or create dedicated "Progress" or "Trends" page
  - [ ] Ensure chart is prominently displayed
  - [ ] Add section header (e.g., "Your Score Trends")

## Dev Notes

### Critical Architecture Requirements

- **Frontend Framework:** React with TypeScript.
- **Charting Library:** Recharts (recommended), Chart.js, or similar.
- **Responsive Design:** Chart must adapt to different screen sizes.
- **Data Transformation:** Convert session data to chart-compatible format.
- **Styling:** Tailwind CSS for container, chart library for chart styling.
- **Performance:** Limit data points if many sessions (e.g., last 20 sessions).

### Technical Implementation Details

**Suggested component structure:**

```
frontend/src/
├── components/
│   ├── ScoreTrendsChart.tsx        # Main chart component
│   └── InsufficientDataMessage.tsx # Message when <2 sessions
├── services/
│   └── sessionService.ts           # API calls for session data
└── types/
    └── session.ts                  # Session and feedback interfaces
```

**Example using Recharts:**

```typescript
// ScoreTrendsChart.tsx
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';

interface SessionWithScore {
  date: Date;
  overallScore: number;
  jobTitle: string;
  company: string;
}

interface Props {
  sessions: SessionWithScore[];
}

const ScoreTrendsChart: React.FC<Props> = ({ sessions }) => {
  if (sessions.length < 2) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">
          You need at least 2 completed interviews with feedback to see your
          score trends.
        </p>
        <button className="mt-4 bg-blue-600 text-white px-4 py-2 rounded">
          Start Interview
        </button>
      </div>
    );
  }

  // Transform data for chart
  const chartData = sessions.map(session => ({
    date: format(session.date, 'MMM dd'),
    fullDate: format(session.date, 'PPP'), // For tooltip
    score: session.overallScore,
    jobTitle: session.jobTitle,
    company: session.company,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow">
          <p className="font-semibold">{data.fullDate}</p>
          <p className="text-sm text-gray-600">
            {data.jobTitle} at {data.company}
          </p>
          <p className="text-lg font-bold text-blue-600">
            Score: {data.score}/100
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full h-96">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis domain={[0, 100]} />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ScoreTrendsChart;
```

**Installation:**

```bash
npm install recharts
npm install date-fns  # For date formatting
```

**Trend direction color coding (advanced):**

```typescript
// Calculate overall trend
const firstScore = sessions[0].overallScore;
const lastScore = sessions[sessions.length - 1].overallScore;
const isImproving = lastScore > firstScore;
const isStable = lastScore === firstScore;

// Use dynamic line color
const lineColor = isImproving ? '#10b981' : isStable ? '#6b7280' : '#ef4444';
```

**Visual design suggestions:**

- **Chart Container:** White background, shadow, rounded corners
- **Axis Labels:** Clear, readable font
- **Line Color:** Blue (default), green (improving), red (declining)
- **Tooltips:** White background, border, shadow, readable text
- **Responsive:** Full width on mobile, fixed height

**Alternative: Chart.js example:**

```typescript
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const data = {
  labels: sessions.map(s => format(s.date, 'MMM dd')),
  datasets: [
    {
      label: 'Overall Score',
      data: sessions.map(s => s.overallScore),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.5)',
    },
  ],
};

const options = {
  responsive: true,
  scales: {
    y: {
      beginAtZero: true,
      max: 100,
    },
  },
};

<Line data={data} options={options} />;
```

### Related Stories

- **Story 6.4:** Score comparison (provides data for chart)
- **Story 6.3:** Performance metrics dashboard (may include chart)
- **Story 5.5:** Feedback retrieval (data source)

### Testing Checklist

- [ ] Chart renders correctly with session data
- [ ] X-axis shows session dates (formatted)
- [ ] Y-axis shows scores (0-100 range)
- [ ] Line connects data points chronologically
- [ ] Tooltips display on hover with correct session details
- [ ] Chart is responsive (adapts to screen size)
- [ ] Insufficient data message displays when <2 sessions with feedback
- [ ] Chart integrates well into dashboard or page layout
- [ ] No errors in browser console
- [ ] Performance is acceptable (no lag when rendering)

### Definition of Done

- [ ] Charting library installed and configured
- [ ] ScoreTrendsChart component implemented
- [ ] Chart displays session scores over time
- [ ] Tooltips implemented with session details
- [ ] Trend direction visualized (color or trend line)
- [ ] Insufficient data message implemented
- [ ] Chart integrated into appropriate page
- [ ] Component is responsive
- [ ] Manual testing completed
- [ ] Code reviewed and merged
