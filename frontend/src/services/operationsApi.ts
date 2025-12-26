import apiClient from './apiClient';

export type OperationStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type OperationResponse = {
  id: string;
  operation_type: string;
  status: OperationStatus;
  result: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export async function fetchOperation(
  operationId: string
): Promise<OperationResponse> {
  const response = await apiClient.get<OperationResponse>(
    `/api/v1/operations/${operationId}`
  );
  return response.data;
}
