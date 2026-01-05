import { useDashboardMetrics } from '../../metrics';
import type { PracticedRole } from '../../metrics';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { setOpenAiApiKey } from '../../users/api/userApi';
import {
  createResume,
  getMyResume,
  updateMyResume,
} from '../../users/api/resumeApi';

function getErrorMessage(error: unknown): string {
  const maybeError = error as {
    response?: { data?: { detail?: { message?: string } } };
    message?: string;
  };

  return (
    maybeError?.response?.data?.detail?.message ||
    maybeError?.message ||
    'Failed to save API key. Please try again.'
  );
}

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
}

function MetricCard({ title, value, subtitle }: MetricCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
      {subtitle && <p className="text-sm text-gray-600 mt-1">{subtitle}</p>}
    </div>
  );
}

interface MostPracticedRolesProps {
  roles: PracticedRole[];
}

function MostPracticedRoles({ roles }: MostPracticedRolesProps) {
  if (roles.length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Most Practiced Roles
        </h3>
        <p className="text-gray-500">
          No interview data yet. Start your first interview to see your most
          practiced roles!
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Most Practiced Roles
      </h3>
      <div className="space-y-3">
        {roles.map((role, index) => (
          <div
            key={`${role.title}-${role.company}-${index}`}
            className="flex justify-between items-center"
          >
            <div>
              <p className="font-medium text-gray-900">{role.title}</p>
              {role.company && (
                <p className="text-sm text-gray-500">{role.company}</p>
              )}
            </div>
            <span className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-medium">
              {role.count} {role.count === 1 ? 'interview' : 'interviews'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

interface ProfileSettingsCardProps {
  apiKey: string;
  onApiKeyChange: (value: string) => void;
  onSave: () => void;
  isSaving: boolean;
  savedMessage: string | null;
  errorMessage: string | null;

  resumeContent: string;
  onResumeChange: (value: string) => void;
  onSaveResume: () => void;
  isSavingResume: boolean;
  resumeSavedMessage: string | null;
  resumeErrorMessage: string | null;
}

function ProfileSettingsCard({
  apiKey,
  onApiKeyChange,
  onSave,
  isSaving,
  savedMessage,
  errorMessage,
  resumeContent,
  onResumeChange,
  onSaveResume,
  isSavingResume,
  resumeSavedMessage,
  resumeErrorMessage,
}: ProfileSettingsCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-lg font-semibold text-gray-900 mb-2">
        Profile Settings
      </h2>
      <p className="text-sm text-gray-600 mb-4">
        Configure your OpenAI API key and resume to enable AI questions and
        feedback.
      </p>

      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700">
            OpenAI API key
          </label>
          <input
            type="password"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
            placeholder="sk-..."
            value={apiKey}
            onChange={e => onApiKeyChange(e.target.value)}
          />
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
          disabled={isSaving || apiKey.trim().length === 0}
          onClick={onSave}
        >
          {isSaving ? 'Saving…' : 'Save API key'}
        </button>

        {savedMessage ? (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {savedMessage}
          </div>
        ) : null}

        {errorMessage ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {errorMessage}
          </div>
        ) : null}

        <p className="text-xs text-gray-500">
          Your key is stored encrypted and never shown again.
        </p>

        <div className="pt-4 border-t border-gray-200" />

        <div>
          <label className="block text-sm font-medium text-gray-700">
            Resume (plain text)
          </label>
          <textarea
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm min-h-[140px]"
            placeholder="Paste your resume here…"
            value={resumeContent}
            onChange={e => onResumeChange(e.target.value)}
          />
        </div>

        <button
          type="button"
          className="inline-flex items-center justify-center bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50"
          disabled={isSavingResume || resumeContent.trim().length === 0}
          onClick={onSaveResume}
        >
          {isSavingResume ? 'Saving…' : 'Save resume'}
        </button>

        {resumeSavedMessage ? (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {resumeSavedMessage}
          </div>
        ) : null}

        {resumeErrorMessage ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {resumeErrorMessage}
          </div>
        ) : null}

        <p className="text-xs text-gray-500">
          Feedback generation requires a resume.
        </p>
      </div>
    </div>
  );
}

/**
 * Dashboard page with performance metrics (protected)
 */
export const Dashboard = () => {
  const { data: metrics, isLoading, isError } = useDashboardMetrics();
  const queryClient = useQueryClient();
  const [apiKey, setApiKey] = useState('');
  const [apiKeySavedMessage, setApiKeySavedMessage] = useState<string | null>(
    null
  );

  const [resumeContent, setResumeContent] = useState('');
  const [resumeSavedMessage, setResumeSavedMessage] = useState<string | null>(
    null
  );
  const [resumeInitialized, setResumeInitialized] = useState(false);

  const resumeQuery = useQuery({
    queryKey: ['resume', 'me'],
    queryFn: getMyResume,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (resumeInitialized) return;
    if (resumeQuery.data === undefined) return;
    setResumeContent(resumeQuery.data?.content || '');
    setResumeInitialized(true);
  }, [resumeInitialized, resumeQuery.data]);

  const saveApiKeyMutation = useMutation({
    mutationFn: (value: string) => setOpenAiApiKey({ api_key: value }),
    onSuccess: data => {
      setApiKey('');
      setApiKeySavedMessage(data.message || 'API key configured successfully');
    },
  });

  const saveResumeMutation = useMutation({
    mutationFn: async (content: string) => {
      if (resumeQuery.data) {
        return updateMyResume({ content });
      }
      return createResume({ content });
    },
    onSuccess: () => {
      setResumeSavedMessage('Resume saved successfully');
      queryClient.invalidateQueries({ queryKey: ['resume', 'me'] });
    },
  });

  const profileSettingsCardProps: ProfileSettingsCardProps = {
    apiKey,
    onApiKeyChange: value => {
      setApiKeySavedMessage(null);
      setApiKey(value);
    },
    onSave: () => saveApiKeyMutation.mutate(apiKey),
    isSaving: saveApiKeyMutation.isPending,
    savedMessage: apiKeySavedMessage,
    errorMessage: saveApiKeyMutation.isError
      ? getErrorMessage(saveApiKeyMutation.error)
      : null,

    resumeContent,
    onResumeChange: value => {
      setResumeSavedMessage(null);
      setResumeContent(value);
    },
    onSaveResume: () => saveResumeMutation.mutate(resumeContent),
    isSavingResume: saveResumeMutation.isPending,
    resumeSavedMessage,
    resumeErrorMessage:
      resumeQuery.isError || saveResumeMutation.isError
        ? getErrorMessage(
            (saveResumeMutation.isError
              ? saveResumeMutation.error
              : resumeQuery.error) as unknown
          )
        : null,
  };

  if (isLoading) {
    return (
      <div className="px-4 py-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Performance Dashboard
        </h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow flex justify-center items-center min-h-[200px]">
            <div
              className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"
              role="status"
              aria-label="Loading dashboard metrics"
            ></div>
          </div>
          <ProfileSettingsCard {...profileSettingsCardProps} />
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="px-4 py-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Performance Dashboard
        </h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            Failed to load dashboard metrics
          </div>
          <ProfileSettingsCard {...profileSettingsCardProps} />
        </div>
      </div>
    );
  }

  if (!metrics || metrics.completed_interviews === 0) {
    return (
      <div className="px-4 py-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Performance Dashboard
        </h1>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-12 rounded-lg shadow text-center">
            <svg
              className="mx-auto h-16 w-16 text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No Data Yet
            </h3>
            <p className="text-gray-600 mb-6">
              Complete your first interview to see your performance metrics
              here.
            </p>
            <Link
              to="/browse-jobs"
              className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-md hover:bg-indigo-700 transition-colors"
            >
              Browse Jobs
            </Link>
          </div>
          <ProfileSettingsCard {...profileSettingsCardProps} />
        </div>
      </div>
    );
  }

  const avgScoreDisplay =
    metrics.average_score !== null ? metrics.average_score.toFixed(1) : 'N/A';

  return (
    <div className="px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Performance Dashboard
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <MetricCard
          title="Completed Interviews"
          value={metrics.completed_interviews}
        />
        <MetricCard
          title="Average Score"
          value={avgScoreDisplay}
          subtitle={
            metrics.average_score === null ? 'No feedback yet' : undefined
          }
        />
        <MetricCard
          title="Questions Answered"
          value={metrics.total_questions_answered}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MostPracticedRoles roles={metrics.most_practiced_roles} />
        <ProfileSettingsCard {...profileSettingsCardProps} />
      </div>
    </div>
  );
};

export default Dashboard;
