/**
 * RetakeBadge component displays a visual indicator for session retake attempts.
 * Shows "Original Attempt" for first sessions (retake_number === 1) and
 * "Attempt #N" for retakes (retake_number > 1).
 */
import { useTranslation } from 'react-i18next';

interface RetakeBadgeProps {
  retakeNumber: number;
  className?: string;
}

export function RetakeBadge({
  retakeNumber,
  className = '',
}: RetakeBadgeProps) {
  const { t } = useTranslation();
  const isOriginal = retakeNumber === 1;

  const badgeClasses = isOriginal
    ? 'bg-blue-100 text-blue-800 border-blue-300'
    : 'bg-purple-100 text-purple-800 border-purple-300';

  const label = isOriginal
    ? t('sessions.detail.originalAttempt')
    : t('sessions.detail.attemptNumber', { number: retakeNumber });

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${badgeClasses} ${className}`}
      aria-label={`This is ${label.toLowerCase()}`}
    >
      {label}
    </span>
  );
}
