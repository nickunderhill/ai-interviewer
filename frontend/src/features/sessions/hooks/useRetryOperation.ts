import { useMutation, useQueryClient } from '@tanstack/react-query';
import { retryOperation } from '../../../services/operationsApi';

export function useRetryOperation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (operationId: string) => retryOperation(operationId),
    onSuccess: newOperation => {
      // Invalidate relevant queries - both operation and session
      queryClient.invalidateQueries({
        queryKey: ['operation', newOperation.id],
      });
      // Note: Session invalidation requires sessionId context
      // The component using this hook should pass sessionId and invalidate ['sessions', sessionId]
    },
  });
}
