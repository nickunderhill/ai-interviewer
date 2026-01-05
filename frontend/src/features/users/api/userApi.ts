/**
 * User-related API calls.
 */
import apiClient from '../../../services/apiClient';

export interface ApiKeySetRequest {
  api_key: string;
}

export interface ApiKeySetResponse {
  message: string;
}

const BASE_URL = '/api/v1/users/me';

/**
 * Set or update the authenticated user's OpenAI API key.
 * Backend stores it encrypted and never returns the key.
 */
export const setOpenAiApiKey = async (
  payload: ApiKeySetRequest
): Promise<ApiKeySetResponse> => {
  const response = await apiClient.put<ApiKeySetResponse>(
    `${BASE_URL}/api-key`,
    payload
  );
  return response.data;
};
