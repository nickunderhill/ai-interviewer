/**
 * Empty state component for when no sessions exist.
 */
import { Link } from 'react-router-dom';

interface EmptyStateProps {
  title?: string;
  message?: string;
  buttonText?: string;
  buttonLink?: string;
}

export const EmptyState = ({
  title = 'No completed interviews yet',
  message = 'Start your first mock interview to track your progress and receive AI-powered feedback!',
  buttonText = 'Start Interview',
  buttonLink = '/browse-jobs',
}: EmptyStateProps) => {
  return (
    <div className="text-center py-12" data-testid="empty-state">
      <svg
        className="mx-auto h-24 w-24 text-gray-400"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
      <h3 className="mt-4 text-lg font-medium text-gray-900">{title}</h3>
      <p className="mt-2 text-sm text-gray-600 max-w-sm mx-auto">{message}</p>
      <div className="mt-6">
        <Link
          to={buttonLink}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {buttonText}
        </Link>
      </div>
    </div>
  );
};
