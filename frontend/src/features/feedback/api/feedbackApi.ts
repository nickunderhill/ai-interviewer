import apiClient from '../../../services/apiClient';
import type { InterviewFeedback } from '../types/feedback';

export async function fetchFeedback(
  sessionId: string
): Promise<InterviewFeedback> {
  const response = await apiClient.get<InterviewFeedback>(
    `/api/v1/sessions/${sessionId}/feedback`
  );
  return response.data;
}
