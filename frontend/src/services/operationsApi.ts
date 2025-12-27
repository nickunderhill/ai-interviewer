import apiClient from './apiClient';

import type { Operation } from '../types/operation';

export type OperationResponse = Operation;

export async function fetchOperation(
  operationId: string
): Promise<OperationResponse> {
  const response = await apiClient.get<OperationResponse>(
    `/api/v1/operations/${operationId}`
  );
  return response.data;
}

export async function retryOperation(operationId: string): Promise<Operation> {
  const response = await apiClient.post<Operation>(
    `/api/v1/operations/${operationId}/retry`
  );
  return response.data;
}
