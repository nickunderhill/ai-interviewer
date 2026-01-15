/**
 * Score Comparison component.
 * Displays chronological session scores with deltas showing improvements/regressions.
 */
import { useTranslation } from 'react-i18next';
import { useSessionsWithFeedback } from '../hooks/useSessionsWithFeedback';
import type {
  SessionScoreWithDelta,
  SessionWithFeedbackScore,
} from '../types/analytics';

function calculateDeltas(
  sessions: SessionWithFeedbackScore[]
): SessionScoreWithDelta[] {
  return sessions.map((session, index) => {
    if (index === 0) {
      return {
        ...session,
        score_delta: undefined,
        delta_direction: 'none' as const,
      };
    }

    const prevScore = sessions[index - 1].overall_score;
    const delta = session.overall_score - prevScore;
    const direction = delta > 0 ? 'up' : delta < 0 ? 'down' : 'none';

    return {
      ...session,
      score_delta: delta,
      delta_direction: direction as 'up' | 'down' | 'none',
    };
  });
}

function formatDate(dateString: string, locale: string): string {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat(locale === 'ua' ? 'uk-UA' : 'en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date);
}

interface ScoreDeltaProps {
  delta?: number;
  direction?: 'up' | 'down' | 'none';
}

function ScoreDelta({ delta, direction }: ScoreDeltaProps) {
  const { t } = useTranslation();

  if (delta === undefined || direction === 'none') {
    return (
      <span className="text-gray-400 text-sm">
        {t('progress.scoreComparison.na')}
      </span>
    );
  }

  const colorClass = direction === 'up' ? 'text-green-600' : 'text-red-600';
  const icon = direction === 'up' ? '↑' : '↓';
  const sign = delta > 0 ? '+' : '';

  return (
    <span
      className={`${colorClass} font-medium text-sm flex items-center gap-1`}
    >
      <span className="text-lg">{icon}</span>
      {sign}
      {delta.toFixed(1)}
    </span>
  );
}

export function ScoreComparison() {
  const { t, i18n } = useTranslation();
  const { data: sessions, isLoading, isError } = useSessionsWithFeedback();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[200px]">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"
          role="status"
          aria-label="Loading score comparison"
        ></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {t('progress.scoreComparison.error')}
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
            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          {t('progress.scoreComparison.needMoreData')}
        </h3>
        <p className="text-gray-600">
          {t('progress.scoreComparison.needMoreDataDescription')}
        </p>
      </div>
    );
  }

  const sessionsWithDeltas = calculateDeltas(sessions);

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          {t('progress.scoreComparison.title')}
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          {t('progress.scoreComparison.description')}
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {t('progress.scoreComparison.date')}
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {t('progress.scoreComparison.jobPosting')}
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {t('progress.scoreComparison.score')}
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {t('progress.scoreComparison.change')}
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sessionsWithDeltas.map(session => (
              <tr
                key={session.session_id}
                className="hover:bg-gray-50 transition-colors"
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {formatDate(session.created_at, i18n.language)}
                </td>
                <td className="px-6 py-4 text-sm">
                  <div>
                    <div className="font-medium text-gray-900">
                      {session.job_posting.title}
                    </div>
                    {session.job_posting.company && (
                      <div className="text-gray-500">
                        {session.job_posting.company}
                      </div>
                    )}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-lg font-semibold text-gray-900">
                    {session.overall_score.toFixed(1)}
                  </span>
                  <span className="text-sm text-gray-500">/100</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <ScoreDelta
                    delta={session.score_delta}
                    direction={session.delta_direction}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ScoreComparison;
