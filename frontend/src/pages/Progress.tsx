/**
 * Progress page combining score comparison and trends.
 */
import { useTranslation } from 'react-i18next';
import { ScoreComparison } from '../features/sessions/components/ScoreComparison';
import { ScoreTrends } from '../features/sessions/components/ScoreTrends';

export function Progress() {
  const { t } = useTranslation();

  return (
    <div className="px-4 py-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {t('progress.title')}
        </h1>
        <p className="text-gray-600">{t('progress.description')}</p>
      </div>

      <ScoreTrends />
      <ScoreComparison />
    </div>
  );
}

export default Progress;
