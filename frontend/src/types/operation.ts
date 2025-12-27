export type OperationStatus = 'pending' | 'processing' | 'completed' | 'failed';

export type OperationType = 'question_generation' | 'feedback_analysis';

export type Operation = {
  id: string;
  operation_type: OperationType;
  status: OperationStatus;
  result: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

export const OPERATION_STATUS_DISPLAY: Record<OperationStatus, string> = {
  pending: 'Queued...',
  processing: 'Processing...',
  completed: 'Completed',
  failed: 'Failed',
};

export const OPERATION_TYPE_DISPLAY: Record<OperationType, string> = {
  question_generation: 'Generating question',
  feedback_analysis: 'Analyzing feedback',
};
