/**
 * QuestionMessage component - displays an interview question.
 */
import type { Message } from '../types/session';
import { formatDistanceToNow } from 'date-fns';

interface QuestionMessageProps {
  message: Message;
}

const questionTypeColors = {
  technical: 'bg-blue-100 text-blue-800',
  behavioral: 'bg-green-100 text-green-800',
  situational: 'bg-purple-100 text-purple-800',
};

export default function QuestionMessage({ message }: QuestionMessageProps) {
  const colorClass = message.question_type
    ? questionTypeColors[message.question_type]
    : 'bg-gray-100 text-gray-800';

  return (
    <div
      className="bg-blue-50 border-l-4 border-blue-500 p-3 sm:p-4 rounded-r-lg mr-0 sm:mr-8"
      data-testid="question-message"
    >
      <div className="flex items-start gap-2 sm:gap-3">
        <span className="text-xl sm:text-2xl" aria-label="Question">
          ❓
        </span>
        <div className="flex-1">
          {message.question_type && (
            <span
              className={`inline-block text-xs font-semibold px-2 py-1 rounded mb-2 ${colorClass}`}
            >
              {message.question_type.toUpperCase()}
            </span>
          )}
          <p className="text-sm sm:text-base text-gray-900 font-medium mb-2">
            {message.content}
          </p>
          <p className="text-xs sm:text-sm text-gray-500">
            {formatDistanceToNow(new Date(message.created_at), {
              addSuffix: true,
            })}
          </p>
        </div>
      </div>
    </div>
  );
}
