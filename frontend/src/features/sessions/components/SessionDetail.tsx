/**
 * SessionDetail page component - displays full session details with Q&A history.
 */
import { useParams, Link } from 'react-router-dom';
import { useSession } from '../hooks/useSession';
import { useMessages } from '../hooks/useMessages';
import JobPostingContext from './JobPostingContext';
import MessageList from './MessageList';
import FeedbackLink from './FeedbackLink';
import { RetakeBadge } from './RetakeBadge';
import { RetakeButton } from './RetakeButton';

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>();
  const {
    data: session,
    isLoading: sessionLoading,
    isError: sessionError,
  } = useSession(id);
  const {
    data: messages,
    isLoading: messagesLoading,
    isError: messagesError,
  } = useMessages(id);

  const isLoading = sessionLoading || messagesLoading;
  const isError = sessionError || messagesError;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {/* Skeleton loading */}
        <div className="space-y-4 sm:space-y-6">
          <div className="animate-pulse">
            <div className="h-6 sm:h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="h-24 sm:h-32 bg-gray-200 rounded mb-6"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-24 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div
          className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded"
          role="alert"
        >
          <p className="text-sm sm:text-base font-semibold">
            Failed to load session
          </p>
          <p className="text-xs sm:text-sm">
            The session could not be found or you don't have permission to view
            it.
          </p>
        </div>
        <Link
          to="/history"
          className="mt-4 inline-block text-sm sm:text-base text-blue-600 hover:text-blue-800"
          aria-label="Back to session history"
        >
          ← Back to Session History
        </Link>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  return (
    <div
      className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8"
      data-testid="session-detail"
    >
      {/* Breadcrumb */}
      <Link
        to="/history"
        className="text-sm sm:text-base text-blue-600 hover:text-blue-800 mb-4 inline-block"
        aria-label="Back to session history"
      >
        ← Back to Session History
      </Link>

      {/* Retake Badge and Session Context */}
      <div className="mb-4">
        <RetakeBadge retakeNumber={session.retake_number} />
        {session.retake_number > 1 && (
          <p className="text-sm text-gray-600 mt-2">
            This is your{' '}
            {session.retake_number === 2
              ? '2nd'
              : session.retake_number === 3
              ? '3rd'
              : `${session.retake_number}th`}{' '}
            attempt at this role
          </p>
        )}
        {session.original_session_id && (
          <Link
            to={`/history?original=${session.original_session_id}`}
            className="inline-flex items-center text-sm text-purple-600 hover:text-purple-700 font-medium mt-2"
          >
            View all attempts →
          </Link>
        )}
        {!session.original_session_id && session.retake_number === 1 && (
          <Link
            to={`/history?original=${session.id}`}
            className="inline-flex items-center text-sm text-purple-600 hover:text-purple-700 font-medium mt-2"
          >
            View all attempts →
          </Link>
        )}
      </div>

      {/* Job Posting Context */}
      <JobPostingContext jobPosting={session.job_posting} />

      {/* Q&A Messages */}
      <div className="mt-6 sm:mt-8">
        <h2 className="text-xl sm:text-2xl font-bold mb-4">
          Interview Questions & Answers
        </h2>
        {messages && messages.length > 0 ? (
          <MessageList messages={messages} />
        ) : (
          <p className="text-gray-500 text-center py-8">
            No messages in this session yet.
          </p>
        )}
      </div>

      {/* Feedback Link and Retake Button */}
      {session.status === 'completed' && (
        <div className="mt-6 space-y-4">
          <FeedbackLink sessionId={session.id} />
          <div className="flex justify-center">
            <RetakeButton sessionId={session.id} />
          </div>
        </div>
      )}
    </div>
  );
}
