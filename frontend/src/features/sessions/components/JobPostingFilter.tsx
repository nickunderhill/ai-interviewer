/**
 * Job Posting Filter component for session filtering.
 */
import { useTranslation } from 'react-i18next';
import { useJobPostings } from '../../jobs/hooks/useJobPostings';

interface JobPostingFilterProps {
  selectedJobPostingId: string;
  onJobPostingChange: (jobPostingId: string) => void;
  onClear: () => void;
}

export function JobPostingFilter({
  selectedJobPostingId,
  onJobPostingChange,
  onClear,
}: JobPostingFilterProps) {
  const { t } = useTranslation();
  const { data: jobPostings, isLoading } = useJobPostings();

  if (isLoading) {
    return (
      <div className="bg-white p-4 rounded-lg shadow">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-3"></div>
          <div className="h-10 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-4 rounded-lg shadow space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">
          {t('sessions.history.filterByJob')}
        </h3>
        {selectedJobPostingId && (
          <button
            onClick={onClear}
            className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
          >
            {t('sessions.history.clear')}
          </button>
        )}
      </div>

      <select
        value={selectedJobPostingId}
        onChange={e => onJobPostingChange(e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">{t('sessions.history.allJobs')}</option>
        {jobPostings?.map(job => (
          <option key={job.id} value={job.id}>
            {job.title}
            {job.company && ` ${t('sessions.historyItem.at')} ${job.company}`}
          </option>
        ))}
      </select>

      {selectedJobPostingId && jobPostings && (
        <div className="text-sm text-gray-600">
          {(() => {
            const selected = jobPostings.find(
              j => j.id === selectedJobPostingId
            );
            return selected ? (
              <span>
                {t('sessions.historyItem.filtering')}{' '}
                <span className="font-medium">{selected.title}</span>
                {selected.company && (
                  <span>
                    {' '}
                    {t('sessions.historyItem.at')} {selected.company}
                  </span>
                )}
              </span>
            ) : null;
          })()}
        </div>
      )}
    </div>
  );
}

export default JobPostingFilter;
