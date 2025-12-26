/**
 * Session History page component.
 * Displays a list of all completed interview sessions.
 */
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useSessions } from '../hooks/useSessions';
import { SessionHistoryItem } from './SessionHistoryItem';
import { EmptyState } from './EmptyState';
import { DateRangeFilter } from './DateRangeFilter';
import { JobPostingFilter } from './JobPostingFilter';

export const SessionHistory = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize from URL params or empty
  const [startDate, setStartDate] = useState(
    searchParams.get('start_date') || ''
  );
  const [endDate, setEndDate] = useState(searchParams.get('end_date') || '');
  const [jobPostingId, setJobPostingId] = useState(
    searchParams.get('job_posting_id') || ''
  );
  const originalSessionId = searchParams.get('original') || '';

  // Sync filters to URL params
  useEffect(() => {
    const params = new URLSearchParams();
    if (startDate) params.set('start_date', startDate);
    if (endDate) params.set('end_date', endDate);
    if (jobPostingId) params.set('job_posting_id', jobPostingId);
    if (originalSessionId) params.set('original', originalSessionId);
    setSearchParams(params, { replace: true });
  }, [startDate, endDate, jobPostingId, originalSessionId, setSearchParams]);

  const {
    data: sessions,
    isLoading,
    isError,
    error,
  } = useSessions({
    status: 'completed',
    startDate: startDate || undefined,
    endDate: endDate || undefined,
    jobPostingId: jobPostingId || undefined,
    originalSessionId: originalSessionId || undefined,
  });

  const handlePresetSelect = (days: number) => {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - days);

    setEndDate(end.toISOString().split('T')[0]);
    setStartDate(start.toISOString().split('T')[0]);
  };

  const handleClearDateFilter = () => {
    setStartDate('');
    setEndDate('');
  };

  const handleClearJobFilter = () => {
    setJobPostingId('');
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Session History
        </h1>
        <div className="space-y-4">
          {/* Loading skeleton matching SessionHistoryItem layout */}
          {[1, 2, 3].map(i => (
            <div
              key={i}
              className="bg-white border border-gray-200 rounded-lg p-6 animate-pulse"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
                <div className="h-6 w-24 bg-gray-200 rounded-full"></div>
              </div>
              <div className="flex gap-6 mb-4">
                <div className="h-4 bg-gray-200 rounded w-32"></div>
                <div className="h-4 bg-gray-200 rounded w-32"></div>
              </div>
              <div className="h-4 bg-gray-200 rounded w-24"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error loading sessions</h3>
          <p className="text-red-600 text-sm mt-1">
            {error instanceof Error
              ? error.message
              : 'An unexpected error occurred'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8" data-testid="session-history">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Session History</h1>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        <DateRangeFilter
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          onClear={handleClearDateFilter}
          onPresetSelect={handlePresetSelect}
        />
        <JobPostingFilter
          selectedJobPostingId={jobPostingId}
          onJobPostingChange={setJobPostingId}
          onClear={handleClearJobFilter}
        />
      </div>

      {/* Results count indicator */}
      {(startDate || endDate || jobPostingId || originalSessionId) &&
        sessions && (
          <div className="mb-4 text-sm text-gray-600">
            {originalSessionId ? (
              <>
                Showing all attempts for this job posting (
                <span className="font-semibold">{sessions.length}</span>{' '}
                {sessions.length === 1 ? 'attempt' : 'attempts'})
              </>
            ) : (
              <>
                Showing <span className="font-semibold">{sessions.length}</span>{' '}
                {sessions.length === 1 ? 'session' : 'sessions'}
                {(startDate || endDate) && ' in date range'}
                {jobPostingId && ' for selected job posting'}
              </>
            )}
          </div>
        )}

      {!sessions || sessions.length === 0 ? (
        <EmptyState />
      ) : (
        <div className="space-y-4" data-testid="session-list">
          {sessions.map(session => (
            <SessionHistoryItem key={session.id} session={session} />
          ))}
        </div>
      )}
    </div>
  );
};
