/**
 * Progress page combining score comparison and trends.
 */
import { ScoreComparison } from '../features/sessions/components/ScoreComparison';
import { ScoreTrends } from '../features/sessions/components/ScoreTrends';

export function Progress() {
  return (
    <div className="px-4 py-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Progress</h1>
        <p className="text-gray-600">
          Track your improvement across interviews
        </p>
      </div>

      <ScoreTrends />
      <ScoreComparison />
    </div>
  );
}

export default Progress;
