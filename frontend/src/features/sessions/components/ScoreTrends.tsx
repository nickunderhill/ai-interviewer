/**
 * Score Trends visualization component.
 * Displays line chart showing score progression over time.
 */
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useSessionsWithFeedback } from '../hooks/useSessionsWithFeedback';

interface ChartDataPoint {
  date: string;
  dateFormatted: string;
  score: number;
  jobTitle: string;
  company: string | null;
}

function formatDateShort(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
  }).format(date);
}

function formatDateLong(dateString: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function CustomTooltip(props: any) {
  if (!props.active || !props.payload || !props.payload.length) {
    return null;
  }

  const data = props.payload[0].payload as ChartDataPoint;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-4">
      <p className="text-sm font-semibold text-gray-900 mb-1">
        {data.dateFormatted}
      </p>
      <p className="text-sm text-gray-700 mb-1">
        <span className="font-medium">{data.jobTitle}</span>
        {data.company && (
          <span className="text-gray-500"> at {data.company}</span>
        )}
      </p>
      <p className="text-lg font-bold text-indigo-600">
        Score: {data.score.toFixed(1)}/100
      </p>
    </div>
  );
}

export function ScoreTrends() {
  const { data: sessions, isLoading, isError } = useSessionsWithFeedback();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[300px]">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"
          role="status"
          aria-label="Loading score trends"
        ></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        Failed to load score trends data
      </div>
    );
  }

  if (!sessions || sessions.length < 2) {
    return (
      <div className="bg-white p-8 rounded-lg shadow text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400 mb-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Need More Data
        </h3>
        <p className="text-gray-600">
          You need at least 2 completed interviews with feedback to see your
          score trends.
        </p>
      </div>
    );
  }

  const chartData: ChartDataPoint[] = sessions.map(session => ({
    date: session.created_at,
    dateFormatted: formatDateLong(session.created_at),
    score: session.overall_score,
    jobTitle: session.job_posting.title,
    company: session.job_posting.company,
  }));

  // Calculate trend direction
  const firstScore = chartData[0].score;
  const lastScore = chartData[chartData.length - 1].score;
  const trendDirection =
    lastScore > firstScore
      ? 'improving'
      : lastScore < firstScore
      ? 'declining'
      : 'stable';
  const lineColor =
    trendDirection === 'improving'
      ? '#10b981'
      : trendDirection === 'declining'
      ? '#ef4444'
      : '#6366f1';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Score Trends</h2>
        <p className="text-sm text-gray-600 mt-1">
          Your performance over time
          {trendDirection !== 'stable' && (
            <span
              className={`ml-2 font-medium ${
                trendDirection === 'improving'
                  ? 'text-green-600'
                  : 'text-red-600'
              }`}
            >
              ({trendDirection === 'improving' ? '↑' : '↓'} {trendDirection})
            </span>
          )}
        </p>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDateShort}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            domain={[0, 100]}
            ticks={[0, 25, 50, 75, 100]}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line
            type="monotone"
            dataKey="score"
            stroke={lineColor}
            strokeWidth={3}
            dot={{ fill: lineColor, strokeWidth: 2, r: 5 }}
            activeDot={{ r: 7 }}
          />
        </LineChart>
      </ResponsiveContainer>

      {sessions.length > 0 && (
        <div className="mt-6 grid grid-cols-3 gap-4 border-t border-gray-200 pt-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">Best Score</p>
            <p className="text-lg font-bold text-gray-900">
              {Math.max(...sessions.map(s => s.overall_score)).toFixed(1)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Average Score</p>
            <p className="text-lg font-bold text-gray-900">
              {(
                sessions.reduce((sum, s) => sum + s.overall_score, 0) /
                sessions.length
              ).toFixed(1)}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Latest Score</p>
            <p className="text-lg font-bold text-gray-900">
              {sessions[sessions.length - 1].overall_score.toFixed(1)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ScoreTrends;
