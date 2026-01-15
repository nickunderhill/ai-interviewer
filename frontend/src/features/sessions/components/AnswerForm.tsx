import { useEffect, useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

import { submitAnswer } from '../api/sessionApi';
import { generateFeedback } from '../../../services/sessionAiApi';
import { useOperationPolling } from '../hooks/useOperationPolling';
import { OperationStatus } from '../../../components/common/OperationStatus';
import { StatusBadge } from '../../../components/common/StatusBadge';
import { ErrorDisplay } from '../../../components/common/ErrorDisplay';

type Props = {
  sessionId: string;
  className?: string;
  onSubmitted?: () => void;
};

export function AnswerForm({ sessionId, className, onSubmitted }: Props) {
  const { t } = useTranslation();
  const MAX_ANSWER_LENGTH = 20000;
  const [answerText, setAnswerText] = useState('');
  const [feedbackOperationId, setFeedbackOperationId] = useState<string | null>(
    null
  );

  const submitMutation = useMutation({
    mutationFn: async () => {
      const trimmed = answerText.trim();
      if (!trimmed) {
        throw new Error('Answer cannot be empty');
      }
      if (trimmed.length > MAX_ANSWER_LENGTH) {
        throw new Error('Answer is too long');
      }
      await submitAnswer(sessionId, trimmed);
      return trimmed;
    },
    onSuccess: () => {
      setAnswerText('');
      onSubmitted?.();
    },
    retry: false,
  });

  const feedbackMutation = useMutation({
    mutationFn: () => generateFeedback(sessionId),
    onSuccess: operation => {
      setFeedbackOperationId(operation.id);
    },
    retry: false,
  });

  // Auto-start feedback analysis after a successful answer submission.
  useEffect(() => {
    if (submitMutation.isSuccess) {
      feedbackMutation.mutate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submitMutation.isSuccess]);

  const {
    operation: feedbackOperation,
    isFetching: feedbackFetching,
    elapsedSeconds,
    showTimeoutWarning,
  } = useOperationPolling(feedbackOperationId);

  const isBusy = submitMutation.isPending || feedbackMutation.isPending;

  const validationMessage = useMemo(() => {
    if (!submitMutation.isError) return null;
    const err = submitMutation.error;
    if (err instanceof Error && err.message === 'Answer cannot be empty') {
      return 'Please enter an answer before submitting.';
    }
    if (err instanceof Error && err.message === 'Answer is too long') {
      return `Your answer is too long. Please keep it under ${MAX_ANSWER_LENGTH.toLocaleString()} characters.`;
    }
    return 'Unable to submit answer.\n\nWhat to do: Try again.';
  }, [MAX_ANSWER_LENGTH, submitMutation.error, submitMutation.isError]);

  const feedbackErrorMessage =
    (feedbackOperation?.status === 'failed' &&
      (feedbackOperation.error_message ||
        'Unable to analyze feedback.\n\nWhat to do: Try again.')) ||
    null;

  return (
    <div className={className ?? ''}>
      <form
        onSubmit={e => {
          e.preventDefault();
          submitMutation.mutate();
        }}
        className="space-y-3"
      >
        <label
          htmlFor="answer"
          className="block text-sm font-medium text-gray-900"
        >
          {t('sessions.answer.label')}
        </label>
        <textarea
          id="answer"
          name="answer"
          value={answerText}
          onChange={e => setAnswerText(e.target.value)}
          maxLength={MAX_ANSWER_LENGTH}
          rows={4}
          className="w-full rounded-lg border border-gray-300 p-3 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder={t('sessions.answer.placeholder')}
          disabled={isBusy}
        />

        {validationMessage ? (
          <ErrorDisplay message={validationMessage} severity="error" />
        ) : null}

        <button
          type="submit"
          className="inline-flex items-center justify-center bg-blue-600 text-white px-4 sm:px-6 py-2 rounded-lg hover:bg-blue-700 font-medium text-sm sm:text-base disabled:opacity-50"
          disabled={isBusy}
        >
          {submitMutation.isPending
            ? t('sessions.answer.submitting')
            : t('sessions.answer.submit')}
        </button>
      </form>

      {feedbackOperation ? (
        <div className="mt-4 flex items-center justify-between gap-4">
          <OperationStatus
            status={feedbackOperation.status}
            operationType={feedbackOperation.operation_type}
            elapsedSeconds={elapsedSeconds}
            showTimeoutWarning={showTimeoutWarning}
          />
          <StatusBadge status={feedbackOperation.status} size="sm" />
        </div>
      ) : null}

      {feedbackErrorMessage ? (
        <div className="mt-3">
          <ErrorDisplay
            message={feedbackErrorMessage}
            onRetry={() => {
              setFeedbackOperationId(null);
              feedbackMutation.mutate();
            }}
            severity="error"
          />
        </div>
      ) : null}

      {feedbackFetching ? (
        <div className="sr-only" aria-live="polite">
          Fetching feedback operation status
        </div>
      ) : null}
    </div>
  );
}
