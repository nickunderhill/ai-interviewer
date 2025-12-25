/**
 * MessageList component - displays chronological list of Q&A messages.
 */
import type { Message } from '../types/session';
import QuestionMessage from './QuestionMessage';
import AnswerMessage from './AnswerMessage';

interface MessageListProps {
  messages: Message[];
}

export default function MessageList({ messages }: MessageListProps) {
  return (
    <div className="space-y-4" data-testid="message-list">
      {messages.map(message => {
        if (message.message_type === 'question') {
          return <QuestionMessage key={message.id} message={message} />;
        }
        return <AnswerMessage key={message.id} message={message} />;
      })}
    </div>
  );
}
