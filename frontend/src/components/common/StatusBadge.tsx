import React from 'react';
import type { OperationStatus } from '../../types/operation';

type Props = {
  status: OperationStatus;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
};

export function StatusBadge({ status, size = 'md', className }: Props) {
  const sizeClasses =
    size === 'sm'
      ? 'text-xs px-2 py-0.5'
      : size === 'lg'
      ? 'text-base px-3 py-1.5'
      : 'text-sm px-2.5 py-1';

  const statusStyles =
    status === 'completed'
      ? 'bg-green-100 text-green-800 border-green-200'
      : status === 'failed'
      ? 'bg-red-100 text-red-800 border-red-200'
      : 'bg-blue-100 text-blue-800 border-blue-200';

  const statusText =
    status === 'pending'
      ? 'Queued'
      : status === 'processing'
      ? 'Processing'
      : status === 'completed'
      ? 'Completed'
      : 'Failed';

  return (
    <span
      className={`inline-flex items-center font-medium border rounded-full ${sizeClasses} ${statusStyles}${
        className ? ` ${className}` : ''
      }`}
      role="status"
      aria-label={`Status: ${statusText}`}
    >
      {statusText}
    </span>
  );
}
