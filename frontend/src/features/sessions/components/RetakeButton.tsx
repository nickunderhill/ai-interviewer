/**
 * RetakeButton component - creates a new interview session as a retake.
 * Only displayed for completed sessions.
 */
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { retakeInterview } from '../api/sessionApi';

interface RetakeButtonProps {
  sessionId: string;
  className?: string;
}

export function RetakeButton({ sessionId, className = '' }: RetakeButtonProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const retakeMutation = useMutation({
    mutationFn: () => retakeInterview(sessionId),
    onSuccess: newSession => {
      // Invalidate sessions list to show new retake
      queryClient.invalidateQueries({ queryKey: ['sessions'] });
      // Navigate to the new session
      navigate(`/sessions/${newSession.id}`);
    },
    onError: (error: unknown) => {
      // Basic error handling - could be enhanced with toast notifications
      console.error('Failed to create retake:', error);
      alert('Failed to create retake. Please try again.');
    },
  });

  return (
    <button
      onClick={e => {
        e.stopPropagation(); // Prevent parent click events (e.g., card clicks)
        retakeMutation.mutate();
      }}
      disabled={retakeMutation.isPending}
      className={`px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${className}`}
      aria-label="Retake this interview"
    >
      {retakeMutation.isPending ? 'Creating...' : 'Retake Interview'}
    </button>
  );
}
