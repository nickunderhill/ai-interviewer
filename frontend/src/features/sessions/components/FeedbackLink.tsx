/**
 * FeedbackLink component - displays link to view feedback if it exists.
 */
import { Link } from 'react-router-dom';
import { useFeedbackStatus } from '../hooks/useFeedbackStatus';

interface FeedbackLinkProps {
  sessionId: string;
  sessionStatus: string;
}

export default function FeedbackLink({
  sessionId,
  sessionStatus,
}: FeedbackLinkProps) {
  const { data: feedbackExists, isLoading } = useFeedbackStatus(sessionId);

  if (sessionStatus !== 'completed') {
    return null;
  }

  if (isLoading) {
    return null; // Don't show anything while checking
  }

  const title = feedbackExists
    ? 'AI Feedback Available'
    : 'Generate AI Feedback';
  const description = feedbackExists
    ? 'Your interview performance has been analyzed. View detailed feedback on your answers.'
    : 'Feedback has not been generated for this session yet.';
  const buttonText = feedbackExists ? 'View Feedback' : 'Generate Feedback';

  return (
    <div className="mt-6 sm:mt-8 p-4 sm:p-6 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>
      <p className="text-sm sm:text-base text-gray-700 mb-4">{description}</p>
      <Link
        to={`/sessions/${sessionId}/feedback`}
        className="inline-block bg-blue-600 text-white px-4 sm:px-6 py-2 rounded-lg hover:bg-blue-700 font-medium text-sm sm:text-base"
        data-testid="view-feedback-link"
        aria-label="View detailed AI feedback for this interview"
      >
        {buttonText}
      </Link>
    </div>
  );
}
