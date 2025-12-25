# Story 7.5: Create Dimension-Level Improvement Tracking

Status: ready-for-dev

## Story

As a user, I want to see how each feedback dimension has improved across
retakes, so that I can identify which skills are getting better.

## Acceptance Criteria

1. **Given** I have multiple retakes with feedback **When** I view
   dimension-level improvement **Then** the frontend displays a comparison table
   or chart showing all 4 dimension scores (Technical Accuracy, Communication
   Clarity, Problem-Solving, Relevance) across all attempts **And** each
   dimension shows the trend (improving, stable, declining) **And** uses visual
   indicators (arrows, color coding) to highlight changes **And** calculates the
   total improvement (latest score - first score) for each dimension **And** if
   data is insufficient, displays an appropriate message ✅

## Tasks / Subtasks

- [ ] Task 1: Update retake chain endpoint to include dimension scores (AC: #1)

  - [ ] Verify feedback response includes dimension_scores field
  - [ ] Ensure dimension_scores is properly serialized in API response
  - [ ] Schema: technical_accuracy, communication_clarity, problem_solving,
        relevance

- [ ] Task 2: Create DimensionComparison component (AC: #1)

  - [ ] Create
        `frontend/src/features/analytics/components/DimensionComparison.tsx`
  - [ ] Display table comparing 4 dimensions across all attempts
  - [ ] Columns: Dimension name, scores per attempt, trend, total improvement
  - [ ] Responsive design for mobile (consider horizontal scroll or card layout)

- [ ] Task 3: Calculate dimension trends (AC: #1)

  - [ ] For each dimension, compare consecutive attempt scores
  - [ ] Determine trend: improving (mostly increases), stable (±2 points),
        declining (mostly decreases)
  - [ ] Calculate total improvement: latest_score - first_score
  - [ ] Calculate average improvement rate if helpful

- [ ] Task 4: Implement visual trend indicators (AC: #1)

  - [ ] Improving: Green color, upward arrow ↑
  - [ ] Stable: Gray color, horizontal arrow →
  - [ ] Declining: Red color, downward arrow ↓
  - [ ] Use icons and color for redundancy (accessibility)
  - [ ] Show numerical change (e.g., "+12" or "-5")

- [ ] Task 5: Create dimension score visualization (AC: #1)

  - [ ] Multi-line chart with one line per dimension
  - [ ] X-axis: Attempt number
  - [ ] Y-axis: Score (0-100)
  - [ ] Different color for each dimension
  - [ ] Legend identifying each dimension
  - [ ] Interactive tooltips showing exact values

- [ ] Task 6: Add dimension score breakdown to each attempt (AC: #1)

  - [ ] Expand/collapse section in ScoreComparison
  - [ ] Show radar chart or bar chart for each attempt's 4 dimensions
  - [ ] Compare current attempt dimensions to previous attempt
  - [ ] Highlight strongest and weakest dimensions

- [ ] Task 7: Handle insufficient data scenarios (AC: #1)

  - [ ] No feedback: "Complete interview to receive feedback"
  - [ ] Only 1 attempt: "Retake to track dimension improvements"
  - [ ] Missing dimension scores: Handle gracefully (display N/A)

- [ ] Task 8: Add insights and recommendations (AC: #1)
  - [ ] Identify strongest improving dimension
  - [ ] Identify dimension needing most work
  - [ ] Show personalized message: "Great progress on Technical Accuracy! Focus
        on improving Communication Clarity."
  - [ ] Link to learning resources based on weak dimensions

## Dev Notes

### Critical Architecture Requirements

**Frontend:**

- **Framework:** React 18+ with TypeScript
- **Chart Library:** Recharts for multi-line charts
- **Styling:** Tailwind CSS v3+
- **State:** TanStack Query
- **Component Location:** `frontend/src/features/analytics/components/`

**Backend:**

- Reuse existing `/api/v1/sessions/{id}/retake-chain` endpoint
- Ensure feedback includes dimension_scores in response

**Dimension Names:**

1. Technical Accuracy (technical_accuracy)
2. Communication Clarity (communication_clarity)
3. Problem-Solving (problem_solving)
4. Relevance (relevance)

### Component Implementation

**DimensionComparison Component:**

```tsx
// frontend/src/features/analytics/components/DimensionComparison.tsx
import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface DimensionComparisonProps {
  sessions: SessionWithFeedback[];
}

interface DimensionTrend {
  name: string;
  displayName: string;
  scores: number[];
  trend: 'improving' | 'stable' | 'declining';
  totalChange: number;
  color: string;
}

const DIMENSION_CONFIG = [
  {
    key: 'technical_accuracy',
    display: 'Technical Accuracy',
    color: '#3b82f6',
  },
  {
    key: 'communication_clarity',
    display: 'Communication Clarity',
    color: '#10b981',
  },
  { key: 'problem_solving', display: 'Problem-Solving', color: '#f59e0b' },
  { key: 'relevance', display: 'Relevance', color: '#8b5cf6' },
];

export function DimensionComparison({ sessions }: DimensionComparisonProps) {
  const dimensionData = useMemo(() => {
    const completedSessions = sessions
      .filter(s => s.status === 'completed' && s.feedback?.dimension_scores)
      .sort((a, b) => a.retake_number - b.retake_number);

    if (completedSessions.length === 0) return null;

    return DIMENSION_CONFIG.map(config => {
      const scores = completedSessions.map(
        s => s.feedback!.dimension_scores[config.key]
      );

      const totalChange = scores[scores.length - 1] - scores[0];
      const trend = calculateTrend(scores);

      return {
        name: config.key,
        displayName: config.display,
        scores,
        trend,
        totalChange,
        color: config.color,
      };
    });
  }, [sessions]);

  const chartData = useMemo(() => {
    if (!dimensionData) return [];

    const attemptCount = dimensionData[0].scores.length;
    return Array.from({ length: attemptCount }, (_, index) => {
      const dataPoint: any = { attempt: index + 1 };
      dimensionData.forEach(dim => {
        dataPoint[dim.name] = dim.scores[index];
      });
      return dataPoint;
    });
  }, [dimensionData]);

  if (!dimensionData || dimensionData[0].scores.length === 0) {
    return (
      <div className="text-center py-8 text-gray-600">
        No feedback data available for dimension comparison.
      </div>
    );
  }

  if (dimensionData[0].scores.length === 1) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600 mb-4">
          Complete more attempts to track dimension-level improvements
        </p>
        <button className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700">
          Retake Interview
        </button>
      </div>
    );
  }

  const strongestDimension = dimensionData.reduce((max, dim) =>
    dim.totalChange > max.totalChange ? dim : max
  );

  const weakestDimension = dimensionData.reduce((min, dim) =>
    dim.totalChange < min.totalChange ? dim : min
  );

  return (
    <div className="space-y-6">
      {/* Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold text-blue-900 mb-2">💡 Insights</h4>
        <p className="text-sm text-blue-800">
          <strong>Strongest improvement:</strong>{' '}
          {strongestDimension.displayName}({strongestDimension.totalChange > 0
            ? '+'
            : ''}
          {strongestDimension.totalChange.toFixed(1)} points)
        </p>
        {weakestDimension.totalChange < 0 && (
          <p className="text-sm text-blue-800 mt-1">
            <strong>Needs focus:</strong> {weakestDimension.displayName}({weakestDimension.totalChange.toFixed(
              1
            )} points)
          </p>
        )}
      </div>

      {/* Multi-line Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Dimension Trends</h3>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="attempt"
              label={{ value: 'Attempt', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              domain={[0, 100]}
              label={{ value: 'Score', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            {dimensionData.map(dim => (
              <Line
                key={dim.name}
                type="monotone"
                dataKey={dim.name}
                name={dim.displayName}
                stroke={dim.color}
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Dimension Comparison Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <h3 className="text-lg font-semibold p-6 pb-4">
          Detailed Dimension Breakdown
        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Dimension
                </th>
                {dimensionData[0].scores.map((_, index) => (
                  <th
                    key={index}
                    className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase"
                  >
                    Attempt {index + 1}
                  </th>
                ))}
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Trend
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                  Total Change
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dimensionData.map(dim => (
                <tr key={dim.name}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {dim.displayName}
                  </td>
                  {dim.scores.map((score, index) => (
                    <td
                      key={index}
                      className="px-6 py-4 whitespace-nowrap text-sm text-center"
                    >
                      {score.toFixed(1)}
                    </td>
                  ))}
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <TrendBadge trend={dim.trend} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center">
                    <ChangeBadge change={dim.totalChange} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Helper: Calculate trend from score array
function calculateTrend(
  scores: number[]
): 'improving' | 'stable' | 'declining' {
  if (scores.length < 2) return 'stable';

  let improvements = 0;
  let declines = 0;

  for (let i = 1; i < scores.length; i++) {
    const diff = scores[i] - scores[i - 1];
    if (diff > 2) improvements++;
    else if (diff < -2) declines++;
  }

  if (improvements > declines) return 'improving';
  if (declines > improvements) return 'declining';
  return 'stable';
}

// Helper component: Trend badge
interface TrendBadgeProps {
  trend: 'improving' | 'stable' | 'declining';
}

function TrendBadge({ trend }: TrendBadgeProps) {
  const config = {
    improving: {
      color: 'text-green-700 bg-green-100',
      icon: '↑',
      label: 'Improving',
    },
    stable: { color: 'text-gray-700 bg-gray-100', icon: '→', label: 'Stable' },
    declining: {
      color: 'text-red-700 bg-red-100',
      icon: '↓',
      label: 'Declining',
    },
  }[trend];

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}
    >
      <span className="mr-1" aria-hidden="true">
        {config.icon}
      </span>
      {config.label}
    </span>
  );
}

// Helper component: Change badge
interface ChangeBadgeProps {
  change: number;
}

function ChangeBadge({ change }: ChangeBadgeProps) {
  const isPositive = change > 0;
  const isNegative = change < 0;

  const colorClasses = isPositive
    ? 'text-green-700 bg-green-100 font-semibold'
    : isNegative
    ? 'text-red-700 bg-red-100 font-semibold'
    : 'text-gray-700 bg-gray-100';

  const sign = isPositive ? '+' : '';

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs ${colorClasses}`}
    >
      {sign}
      {change.toFixed(1)}
    </span>
  );
}
```

**Integration with ScoreComparison:**

```tsx
// In frontend/src/features/analytics/components/ScoreComparison.tsx
import { DimensionComparison } from './DimensionComparison';

export function ScoreComparison({ sessions }: Props) {
  // ... existing overall score comparison code ...

  return (
    <div className="space-y-8">
      {/* Overall Score Comparison (existing) */}
      <div>{/* ... existing chart and table ... */}</div>

      {/* Dimension-Level Comparison (new) */}
      <div>
        <h2 className="text-xl font-semibold mb-4">Skill Dimension Analysis</h2>
        <DimensionComparison sessions={sessions} />
      </div>
    </div>
  );
}
```

### Type Definitions

```typescript
// frontend/src/features/analytics/types/index.ts
export interface DimensionScores {
  technical_accuracy: number;
  communication_clarity: number;
  problem_solving: number;
  relevance: number;
}

export interface Feedback {
  id: string;
  session_id: string;
  overall_score: number;
  dimension_scores: DimensionScores;
  knowledge_gaps: string[];
  learning_recommendations: string[];
  created_at: string;
}

export interface SessionWithFeedback {
  id: string;
  user_id: string;
  job_posting_id: string | null;
  status: 'active' | 'completed';
  retake_number: number;
  original_session_id: string | null;
  created_at: string;
  feedback?: Feedback;
}
```

### Backend Verification

Ensure existing endpoint includes dimension_scores:

```python
# In backend/app/schemas/feedback.py (should already exist from Epic 5)
class FeedbackResponse(BaseModel):
    id: UUID
    session_id: UUID
    overall_score: float
    dimension_scores: Dict[str, float]  # Must include all 4 dimensions
    knowledge_gaps: List[str]
    learning_recommendations: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### Testing Checklist

**Component Tests:**

- [ ] DimensionComparison renders with multiple sessions
- [ ] DimensionComparison shows single attempt message
- [ ] DimensionComparison shows no data message
- [ ] Trend calculation works correctly
- [ ] Total change calculation works correctly
- [ ] Chart renders with all 4 dimension lines
- [ ] Table displays all dimensions and attempts

**Data Tests:**

- [ ] Test improving trend detection
- [ ] Test stable trend detection
- [ ] Test declining trend detection
- [ ] Test total change calculation (positive/negative/zero)
- [ ] Test with missing dimension scores

**Integration Tests:**

- [ ] Dimension comparison displays in session detail
- [ ] Data fetches correctly from retake chain endpoint
- [ ] Integration with overall score comparison
- [ ] Responsive design on mobile/tablet/desktop

### Visual Design Guidelines

**Colors:**

- Technical Accuracy: Blue (#3b82f6)
- Communication Clarity: Green (#10b981)
- Problem-Solving: Amber (#f59e0b)
- Relevance: Purple (#8b5cf6)

**Trends:**

- Improving: Green badge with ↑
- Stable: Gray badge with →
- Declining: Red badge with ↓

**Layout:**

- Insights card at top
- Multi-line chart showing all dimensions
- Detailed table below chart
- Responsive: stack on mobile, side-by-side on desktop

### Project Structure References

**Files to Create:**

- `frontend/src/features/analytics/components/DimensionComparison.tsx`

**Files to Modify:**

- `frontend/src/features/analytics/components/ScoreComparison.tsx` - Add
  dimension section
- `frontend/src/features/analytics/types/index.ts` - Add DimensionScores type

**Files to Verify:**

- `backend/app/schemas/feedback.py` - Ensure dimension_scores in response
- `backend/app/api/v1/sessions.py` - Verify retake chain includes feedback

**Dependencies:**

- Story 7.1: Retake fields
- Story 7.2: Retake endpoint
- Story 7.4: Retake chain endpoint
- Epic 5: Feedback system with dimension scores

### Related Context

**From Project Context
([project-context.md](../_bmad-output/project-context.md)):**

- React functional components with TypeScript
- Recharts for data visualization
- Tailwind CSS for consistent styling
- TanStack Query for data fetching

**From Architecture ([architecture.md](../_bmad-output/architecture.md)):**

- Feedback includes 4-dimension scoring
- Analytics module for performance tracking
- Multi-dimensional analysis is core feature

**From Epic 7 ([epics.md](../_bmad-output/epics.md)):**

- Story 7.5 completes dimension-level tracking
- Enables identification of specific skill improvements
- Final story in Epic 7 retake feature set

**From Epic 5 (Feedback):**

- Feedback model includes dimension_scores
- 4 dimensions: technical_accuracy, communication_clarity, problem_solving,
  relevance
- Scores range 0-100

### Anti-Patterns to Avoid

❌ Don't hardcode dimension names - use configuration array  
❌ Don't forget to handle missing dimension_scores gracefully  
❌ Don't calculate trends on backend - frontend provides flexibility  
❌ Don't use same color for all dimensions - distinguish with unique colors  
❌ Don't forget mobile responsiveness for chart and table  
❌ Don't show insights without at least 2 attempts

## Dev Agent Record

### Agent Model Used

_To be filled by dev agent_

### Debug Log References

_To be filled by dev agent_

### Completion Notes List

_To be filled by dev agent_

### File List

_To be filled by dev agent_
