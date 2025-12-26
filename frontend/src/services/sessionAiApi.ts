import apiClient from './apiClient';
import type { OperationResponse } from './operationsApi';

export async function generateQuestion(
  sessionId: string
): Promise<OperationResponse> {
  const response = await apiClient.post<OperationResponse>(
    `/api/v1/sessions/${sessionId}/generate-question`
  );
  return response.data;
}

export async function generateFeedback(
  sessionId: string
): Promise<OperationResponse> {
  const response = await apiClient.post<OperationResponse>(
    `/api/v1/sessions/${sessionId}/generate-feedback`
  );
  return response.data;
}
