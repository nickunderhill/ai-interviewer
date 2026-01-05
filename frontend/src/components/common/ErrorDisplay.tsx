export type ErrorDisplaySeverity = 'error' | 'warning' | 'info';

export type ErrorDisplayProps = {
  message: string;
  onRetry?: () => void;
  severity?: ErrorDisplaySeverity;
  className?: string;
};

function splitMessage(message: string): { main: string; action?: string } {
  const parts = message.split(/What to do:/i);
  const main = parts[0]?.trim() ?? '';
  const action = parts.slice(1).join('What to do:').trim();
  return action ? { main, action } : { main };
}

function SeverityIcon({ severity }: { severity: ErrorDisplaySeverity }) {
  const iconClass =
    severity === 'warning'
      ? 'text-orange-600'
      : severity === 'info'
      ? 'text-blue-600'
      : 'text-red-600';

  return (
    <svg
      className={`h-5 w-5 mt-0.5 flex-shrink-0 ${iconClass}`}
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-11a1 1 0 00-1 1v3a1 1 0 102 0V8a1 1 0 00-1-1zm0 8a1.25 1.25 0 100-2.5A1.25 1.25 0 0010 15z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function ErrorDisplay({
  message,
  onRetry,
  severity = 'error',
  className,
}: ErrorDisplayProps) {
  const severityStyles =
    severity === 'warning'
      ? 'bg-orange-50 border-orange-200 text-orange-800'
      : severity === 'info'
      ? 'bg-blue-50 border-blue-200 text-blue-800'
      : 'bg-red-50 border-red-200 text-red-800';

  const { main, action } = splitMessage(message);

  return (
    <div
      className={`border rounded-lg p-4 ${severityStyles}${
        className ? ` ${className}` : ''
      }`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <SeverityIcon severity={severity} />
        <div className="flex-1">
          <p className="font-medium">{main || 'Something went wrong.'}</p>

          {action ? (
            <div className="mt-2">
              <p className="text-sm font-semibold">What to do:</p>
              <ul className="mt-1 list-disc pl-5 text-sm">
                <li>{action}</li>
              </ul>
            </div>
          ) : null}

          {onRetry ? (
            <div className="mt-3">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 text-sm font-medium"
              >
                Retry
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
