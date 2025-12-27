import { useEffect, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchOperation } from '../../../services/operationsApi';
import type { Operation } from '../../../types/operation';

export function useOperationPolling(operationId: string | null) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const operationIdRef = useRef<string | null>(null);
  const statusRef = useRef<Operation['status'] | undefined>(undefined);
  const lastOperationIdRef = useRef<string | null>(null);
  const elapsedSecondsRef = useRef(0);

  const query = useQuery({
    queryKey: ['operations', operationId],
    queryFn: () => fetchOperation(operationId!),
    enabled: !!operationId,
    retry: false,
    refetchInterval: queryContext => {
      const data = queryContext.state.data as Operation | undefined;
      if (!data) return 2500;
      if (data.status === 'pending' || data.status === 'processing')
        return 2500;
      return false;
    },
    refetchOnWindowFocus: false,
  });

  const status = query.data?.status;
  const isProcessing = status === 'pending' || status === 'processing';

  useEffect(() => {
    operationIdRef.current = operationId;
    statusRef.current = status;
  }, [operationId, status]);

  useEffect(() => {
    elapsedSecondsRef.current = elapsedSeconds;
  }, [elapsedSeconds]);

  useEffect(() => {
    const interval = window.setInterval(() => {
      const currentOperationId = operationIdRef.current;
      const currentStatus = statusRef.current;
      const isActiveNow =
        !!currentOperationId &&
        currentStatus !== 'completed' &&
        currentStatus !== 'failed';

      if (!isActiveNow) {
        if (elapsedSecondsRef.current !== 0) {
          setElapsedSeconds(0);
        }
        lastOperationIdRef.current = currentOperationId;
        return;
      }

      // Reset the timer when a new operation begins.
      if (currentOperationId !== lastOperationIdRef.current) {
        lastOperationIdRef.current = currentOperationId;
        setElapsedSeconds(1);
        return;
      }

      setElapsedSeconds(prev => prev + 1);
    }, 1000);

    return () => window.clearInterval(interval);
  }, []);

  const showTimeoutWarning =
    !!operationId &&
    status !== 'completed' &&
    status !== 'failed' &&
    elapsedSeconds >= 30;

  return {
    operation: query.data as Operation | undefined,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    isError: query.isError,
    error: query.error,
    elapsedSeconds,
    showTimeoutWarning,
    isProcessing,
  };
}
