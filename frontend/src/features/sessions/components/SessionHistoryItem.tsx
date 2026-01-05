/**
 * Session history list item component.
 * Displays a single completed session with its details.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { deleteSession } from '../api/sessionApi';
import type { Session } from '../types/session';
import { RetakeBadge } from './RetakeBadge';
import { RetakeButton } from './RetakeButton';

interface SessionHistoryItemProps {
  session: Session;
}

/**
 * Format date to readable format (e.g., "Dec 25, 2025").
 */
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const SessionHistoryItem = ({ session }: SessionHistoryItemProps) => {
  const queryClient = useQueryClient();

  const deleteMutation = useMutation({
    mutationFn: () => deleteSession(session.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
    },
    onError: (error: unknown) => {
      console.error('Failed to delete session:', error);
      alert('Failed to remove this attempt. Please try again.');
    },
  });

  return (
    <div
      className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
      data-testid="session-item"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            {session.job_posting.title}
          </h3>
          <p className="text-sm text-gray-600">{session.job_posting.company}</p>
        </div>
        <div className="flex flex-col gap-2 items-end">
          <RetakeBadge retakeNumber={session.retake_number} />
          <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
            Completed
          </span>
        </div>
      </div>

      <div className="flex gap-6 text-sm text-gray-600 mb-4">
        <div>
          <span className="font-medium">Completed:</span>{' '}
          {formatDate(session.updated_at)}
        </div>
        <div>
          <span className="font-medium">Questions Answered:</span>{' '}
          {session.current_question_number}
        </div>
      </div>

      <div className="flex gap-4 items-center flex-wrap">
        <Link
          to={`/sessions/${session.id}`}
          className="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium"
        >
          View Details
          <svg
            className="ml-2 w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </Link>

        {session.original_session_id && session.retake_number > 1 && (
          <Link
            to={`/history?original=${session.original_session_id}`}
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            View all attempts
          </Link>
        )}

        {session.retake_number === 1 && (
          <Link
            to={`/history?original=${session.id}`}
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            View all attempts
          </Link>
        )}

        <div className="ml-auto flex items-center gap-3">
          <button
            type="button"
            onClick={() => deleteMutation.mutate()}
            disabled={deleteMutation.isPending}
            className="text-sm font-medium text-red-600 hover:text-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
            aria-label="Remove this attempt from history"
          >
            {deleteMutation.isPending ? 'Removing…' : 'Remove'}
          </button>
          <RetakeButton sessionId={session.id} />
        </div>
      </div>
    </div>
  );
};
