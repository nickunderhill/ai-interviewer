import React from 'react';

type Props = {
  message: string;
  subMessage?: string;
  elapsedSeconds?: number;
  showTimeoutWarning?: boolean;
  className?: string;
};

export function ProcessingIndicator({
  message,
  subMessage,
  elapsedSeconds = 0,
  showTimeoutWarning = false,
  className,
}: Props) {
  return (
    <div
      className={`flex flex-col items-center justify-center py-10 ${
        className ?? ''
      }`}
      role="status"
      aria-live="polite"
    >
      <svg
        className="h-10 w-10 animate-spin text-blue-600"
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

      <p className="mt-3 text-lg font-medium text-gray-900">{message}</p>
      {subMessage ? (
        <p className="mt-1 text-sm text-gray-600">{subMessage}</p>
      ) : null}

      {elapsedSeconds > 10 ? (
        <p className="mt-3 text-sm text-gray-600">{elapsedSeconds} seconds</p>
      ) : null}

      {showTimeoutWarning ? (
        <p className="mt-1 text-sm text-orange-600">
          Taking longer than expected. Still processing...
        </p>
      ) : null}
    </div>
  );
}
