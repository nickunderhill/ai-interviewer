import { useEffect, useMemo, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import DimensionScores from './DimensionScores';
import KnowledgeGaps from './KnowledgeGaps';
import LearningRecommendations from './LearningRecommendations';
import { ErrorDisplay } from '../../../components/common/ErrorDisplay';
import { fetchFeedback } from '../api/feedbackApi';
import { generateFeedback } from '../../../services/sessionAiApi';
import {
  fetchOperation,
  type OperationResponse,
} from '../../../services/operationsApi';

export default function FeedbackView() {
  const { id } = useParams<{ id: string }>();
  const sessionId = id ?? '';

  const [operationId, setOperationId] = useState<string | null>(null);

  const feedbackQuery = useQuery({
    queryKey: ['sessions', sessionId, 'feedback'],
    queryFn: () => fetchFeedback(sessionId),
    enabled: !!sessionId,
    retry: false,
  });

  const feedbackNotFound = useMemo(() => {
    const error = feedbackQuery.error as unknown;
    if (!error || typeof error !== 'object' || !('response' in error)) {
      return false;
    }
    const axiosError = error as {
      response?: { status?: number; data?: { detail?: { code?: string } } };
    };

    return (
      axiosError.response?.status === 404 &&
      axiosError.response?.data?.detail?.code === 'FEEDBACK_NOT_FOUND'
    );
  }, [feedbackQuery.error]);

  const generateMutation = useMutation({
    mutationFn: () => generateFeedback(sessionId),
    onSuccess: operation => {
      setOperationId(operation.id);
    },
  });

  const operationQuery = useQuery({
    queryKey: ['operations', operationId],
    queryFn: () => fetchOperation(operationId!),
    enabled: !!operationId,
    retry: false,
    refetchInterval: query => {
      const data = query.state.data as OperationResponse | undefined;
      if (!data) return 1000;
      if (data.status === 'pending' || data.status === 'processing')
        return 1000;
      return false;
    },
  });

  useEffect(() => {
    if (operationQuery.data?.status === 'completed') {
      void feedbackQuery.refetch();
    }
  }, [feedbackQuery, operationQuery.data?.status]);

  const operationFailed = operationQuery.data?.status === 'failed';
  const operationErrorMessage =
    operationQuery.data?.error_message ||
    'Unable to generate feedback.\n\nWhat to do: Try again.';

  const showGenerateSection =
    feedbackNotFound || (!feedbackQuery.data && !feedbackQuery.isLoading);

  if (!id) {
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
      <Link
        to={`/sessions/${id}`}
        className="text-sm sm:text-base text-blue-600 hover:text-blue-800 mb-4 inline-block"
      >
        ← Back to Session
      </Link>
      <h1 className="text-2xl font-bold text-gray-900">Feedback</h1>

      {feedbackQuery.isLoading && (
        <div className="mt-6" aria-label="Loading feedback">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/3" />
            <div className="h-24 bg-gray-200 rounded" />
            <div className="h-24 bg-gray-200 rounded" />
          </div>
        </div>
      )}

      {feedbackQuery.isError && !feedbackNotFound && (
        <div className="mt-6">
          <ErrorDisplay
            message={
              'Failed to load feedback.\n\nWhat to do: Try again. If the problem persists, return to your session and try again.'
            }
            onRetry={() => void feedbackQuery.refetch()}
            severity="error"
          />
        </div>
      )}

      {showGenerateSection && (
        <div className="mt-6 space-y-4">
          {operationFailed && (
            <ErrorDisplay
              message={operationErrorMessage}
              onRetry={() => {
                setOperationId(null);
                generateMutation.mutate();
              }}
              severity="error"
            />
          )}

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-gray-700">
              Feedback has not been generated for this session yet.
            </p>
            <button
              type="button"
              className="mt-3 inline-flex items-center justify-center bg-blue-600 text-white px-4 sm:px-6 py-2 rounded-lg hover:bg-blue-700 font-medium text-sm sm:text-base disabled:opacity-50"
              onClick={() => {
                setOperationId(null);
                generateMutation.mutate();
              }}
              disabled={generateMutation.isPending || operationQuery.isFetching}
            >
              {generateMutation.isPending || operationQuery.isFetching
                ? 'Generating...'
                : 'Generate Feedback'}
            </button>
          </div>
        </div>
      )}

      {feedbackQuery.data && (
        <div className="mt-6 space-y-8">
          <div className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6">
            <DimensionScores
              overallScore={feedbackQuery.data.overall_score}
              technicalAccuracy={feedbackQuery.data.technical_accuracy_score}
              communicationClarity={
                feedbackQuery.data.communication_clarity_score
              }
              problemSolving={feedbackQuery.data.problem_solving_score}
              relevance={feedbackQuery.data.relevance_score}
            />
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6 space-y-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Detailed Feedback
              </h2>
              <p className="text-gray-700 mt-2">
                {feedbackQuery.data.overall_comments ||
                  'Review the notes below for detailed feedback.'}
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Technical Accuracy
                </h3>
                <p className="text-gray-700 mt-1">
                  {feedbackQuery.data.technical_feedback}
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Communication Clarity
                </h3>
                <p className="text-gray-700 mt-1">
                  {feedbackQuery.data.communication_feedback}
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Problem Solving
                </h3>
                <p className="text-gray-700 mt-1">
                  {feedbackQuery.data.problem_solving_feedback}
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  Relevance
                </h3>
                <p className="text-gray-700 mt-1">
                  {feedbackQuery.data.relevance_feedback}
                </p>
              </div>
            </div>
          </div>

          <div className="grid gap-8">
            <div className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6">
              <KnowledgeGaps
                knowledgeGaps={feedbackQuery.data.knowledge_gaps}
              />
            </div>
            <div className="bg-white border border-gray-200 rounded-lg p-4 sm:p-6">
              <LearningRecommendations
                learningRecommendations={
                  feedbackQuery.data.learning_recommendations
                }
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
