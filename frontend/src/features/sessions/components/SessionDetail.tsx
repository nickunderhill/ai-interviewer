/**
 * SessionDetail page component - displays full session details with Q&A history.
 */
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useSession } from '../hooks/useSession';
import { useMessages } from '../hooks/useMessages';
import JobPostingContext from './JobPostingContext';
import MessageList from './MessageList';
import FeedbackLink from './FeedbackLink';
import { RetakeBadge } from './RetakeBadge';
import { RetakeButton } from './RetakeButton';
import { ErrorDisplay } from '../../../components/common/ErrorDisplay';
import { OperationStatus } from '../../../components/common/OperationStatus';
import { StatusBadge } from '../../../components/common/StatusBadge';
import { generateQuestion } from '../../../services/sessionAiApi';
import { useOperationPolling } from '../hooks/useOperationPolling';
import { AnswerForm } from './AnswerForm';
import { completeSession } from '../api/sessionApi';

export default function SessionDetail() {
  const { id } = useParams<{ id: string }>();

  const [questionOperationId, setQuestionOperationId] = useState<string | null>(
    null
  );

  const {
    data: session,
    isLoading: sessionLoading,
    isError: sessionError,
    refetch: refetchSession,
  } = useSession(id);
  const {
    data: messages,
    isLoading: messagesLoading,
    isError: messagesError,
    refetch: refetchMessages,
  } = useMessages(id);

  const isLoading = sessionLoading || messagesLoading;
  const isError = sessionError || messagesError;

  const generateQuestionMutation = useMutation({
    mutationFn: () => generateQuestion(id!),
    onSuccess: operation => {
      setQuestionOperationId(operation.id);
    },
  });

  const completeSessionMutation = useMutation({
    mutationFn: () => completeSession(id!),
    onSuccess: () => {
      void refetchSession();
    },
  });

  const {
    operation: questionOperation,
    isFetching: questionOperationFetching,
    elapsedSeconds: questionElapsedSeconds,
    showTimeoutWarning: questionTimeoutWarning,
  } = useOperationPolling(questionOperationId);

  useEffect(() => {
    if (questionOperation?.status === 'completed') {
      void refetchMessages();
      void refetchSession();
    }
  }, [questionOperation?.status, refetchMessages, refetchSession]);

  const questionOperationFailed = questionOperation?.status === 'failed';
  const questionOperationErrorMessage =
    questionOperation?.error_message ||
    'Unable to generate question.\n\nWhat to do: Try again.';

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
    const handleRetry = () => {
      void refetchSession();
      void refetchMessages();
    };

    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <ErrorDisplay
          message={
            'Failed to load session.\n\nWhat to do: Try again. If the problem persists, return to your session history and try again.'
          }
          onRetry={handleRetry}
          severity="error"
        />
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
        <div className="flex flex-wrap items-center gap-3">
          <RetakeBadge retakeNumber={session.retake_number} />

          {session.original_session_id && (
            <Link
              to={`/history?original=${session.original_session_id}`}
              className="inline-flex items-center text-sm text-purple-600 hover:text-purple-700 font-medium"
            >
              View all attempts →
            </Link>
          )}
          {!session.original_session_id && session.retake_number === 1 && (
            <Link
              to={`/history?original=${session.id}`}
              className="inline-flex items-center text-sm text-purple-600 hover:text-purple-700 font-medium"
            >
              View all attempts →
            </Link>
          )}
        </div>
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
      </div>

      {/* Job Posting Context */}
      <JobPostingContext jobPosting={session.job_posting} />

      <FeedbackLink sessionId={session.id} sessionStatus={session.status} />

      {/* Q&A Messages */}
      <div className="mt-6 sm:mt-8">
        <h2 className="text-xl sm:text-2xl font-bold mb-4">
          Interview Questions & Answers
        </h2>

        {session.status === 'active' && (
          <div className="mb-4 space-y-3">
            {questionOperation ? (
              <div className="flex items-center justify-between gap-4">
                <OperationStatus
                  status={questionOperation.status}
                  operationType={questionOperation.operation_type}
                  elapsedSeconds={questionElapsedSeconds}
                  showTimeoutWarning={questionTimeoutWarning}
                />
                <StatusBadge status={questionOperation.status} size="sm" />
              </div>
            ) : null}

            {questionOperationFailed && (
              <ErrorDisplay
                message={questionOperationErrorMessage}
                onRetry={() => {
                  setQuestionOperationId(null);
                  generateQuestionMutation.mutate();
                }}
                severity="error"
              />
            )}

            <button
              type="button"
              className="inline-flex items-center justify-center bg-blue-600 text-white px-4 sm:px-6 py-2 rounded-lg hover:bg-blue-700 font-medium text-sm sm:text-base disabled:opacity-50"
              onClick={() => {
                setQuestionOperationId(null);
                generateQuestionMutation.mutate();
              }}
              disabled={
                generateQuestionMutation.isPending || questionOperationFetching
              }
            >
              {generateQuestionMutation.isPending || questionOperationFetching
                ? 'Generating...'
                : 'Generate Next Question'}
            </button>
          </div>
        )}

        {(session.status === 'active' || session.status === 'paused') && (
          <div className="mb-4 space-y-3">
            {completeSessionMutation.isError ? (
              <ErrorDisplay
                message={
                  'Unable to complete session.\n\nWhat to do: Try again.'
                }
                onRetry={() => completeSessionMutation.mutate()}
                severity="error"
              />
            ) : null}

            <button
              type="button"
              className="inline-flex items-center justify-center bg-gray-100 text-gray-900 border border-gray-300 px-4 sm:px-6 py-2 rounded-lg hover:bg-gray-200 font-medium text-sm sm:text-base disabled:opacity-50"
              onClick={() => completeSessionMutation.mutate()}
              disabled={completeSessionMutation.isPending}
              aria-label="Complete session"
            >
              {completeSessionMutation.isPending
                ? 'Completing...'
                : 'Complete Session'}
            </button>
          </div>
        )}

        {messages && messages.length > 0 ? (
          <div className="space-y-6">
            <MessageList messages={messages} />

            {session.status === 'active' &&
            messages[messages.length - 1]?.message_type === 'question' ? (
              <div className="border border-gray-200 rounded-lg p-4 sm:p-6">
                <AnswerForm
                  sessionId={session.id}
                  onSubmitted={() => {
                    void refetchMessages();
                  }}
                />
              </div>
            ) : null}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No messages in this session yet.
          </p>
        )}
      </div>

      {/* Retake Button */}
      {session.status === 'completed' && (
        <div className="mt-6 flex justify-center">
          <RetakeButton sessionId={session.id} />
        </div>
      )}
    </div>
  );
}
