/**
 * AnswerMessage component - displays user's answer.
 */
import type { Message } from '../types/session';
import { formatDistanceToNow } from 'date-fns';

interface AnswerMessageProps {
  message: Message;
}

export default function AnswerMessage({ message }: AnswerMessageProps) {
  return (
    <div
      className="bg-gray-50 border-r-4 border-gray-400 p-3 sm:p-4 rounded-l-lg ml-0 sm:ml-8"
      data-testid="answer-message"
    >
      <div className="flex items-start gap-2 sm:gap-3 flex-row-reverse">
        <span className="text-xl sm:text-2xl" aria-label="Answer">
          💬
        </span>
        <div className="flex-1 text-right">
          <p className="text-sm sm:text-base text-gray-900 mb-2 whitespace-pre-wrap text-left">
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
