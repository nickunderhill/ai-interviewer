import { useTranslation } from 'react-i18next';
import type { OperationStatus, OperationType } from '../../types/operation';

type Props = {
  status: OperationStatus;
  operationType: OperationType;
  elapsedSeconds?: number;
  showTimeoutWarning?: boolean;
  className?: string;
};

function SpinnerIcon() {
  return (
    <svg
      className="h-5 w-5 animate-spin text-blue-600"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg
      className="h-5 w-5 text-green-600"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.707a1 1 0 00-1.414-1.414L9 10.172 7.707 8.879a1 1 0 10-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function ErrorIcon() {
  return (
    <svg
      className="h-5 w-5 text-red-600"
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm2.707-10.707a1 1 0 00-1.414-1.414L10 7.586 8.707 6.293a1 1 0 00-1.414 1.414L8.586 9l-1.293 1.293a1 1 0 101.414 1.414L10 10.414l1.293 1.293a1 1 0 001.414-1.414L11.414 9l1.293-1.293z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function getStatusText(
  status: OperationStatus,
  operationType: OperationType,
  t: (key: string) => string
): string {
  if (operationType === 'question_generation') {
    if (status === 'completed') return t('operation.questionReady');
    if (status === 'failed') return t('operation.generationFailed');
    return t('operation.generatingQuestion');
  }

  if (operationType === 'feedback_analysis') {
    if (status === 'completed') return t('operation.feedbackReady');
    if (status === 'failed') return t('operation.analysisFailed');
    return t('operation.analyzingFeedback');
  }

  return status;
}

export function OperationStatus({
  status,
  operationType,
  elapsedSeconds = 0,
  showTimeoutWarning = false,
  className,
}: Props) {
  const { t } = useTranslation();

  const statusColorClass =
    status === 'completed'
      ? 'text-green-700'
      : status === 'failed'
      ? 'text-red-700'
      : 'text-blue-700';

  return (
    <div
      className={`flex items-center gap-3 ${className ?? ''}`}
      role="status"
      aria-live="polite"
    >
      {status === 'pending' || status === 'processing' ? (
        <SpinnerIcon />
      ) : status === 'completed' ? (
        <CheckIcon />
      ) : (
        <ErrorIcon />
      )}

      <div>
        <p className={`font-medium ${statusColorClass}`}>
          {getStatusText(status, operationType, t)}
        </p>

        {(status === 'pending' || status === 'processing') &&
        elapsedSeconds > 10 ? (
          <p className="mt-1 text-sm text-gray-600">
            {elapsedSeconds} {t('operation.seconds')}
          </p>
        ) : null}

        {showTimeoutWarning ? (
          <p className="mt-1 text-sm text-orange-600">
            {t('operation.takingLonger')}
          </p>
        ) : null}
      </div>
    </div>
  );
}
