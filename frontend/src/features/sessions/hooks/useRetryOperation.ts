import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { retryOperation } from '@/services/operationsApi';

export function useRetryOperation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (operationId: string) => retryOperation(operationId),
    onSuccess: newOperation => {
      toast.success('Retrying operation...');

      // Invalidate relevant queries - both operation and session
      queryClient.invalidateQueries({
        queryKey: ['operation', newOperation.id],
      });
      // Note: Session invalidation requires sessionId context
      // The component using this hook should pass sessionId and invalidate ['sessions', sessionId]
    },
    onError: (error: Error) => {
      const message = error.message || 'Failed to retry operation';
      toast.error(message);
    },
  });
}
