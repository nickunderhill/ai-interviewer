import { useDashboardMetrics } from '../../metrics';
import type { PracticedRole } from '../../metrics';

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
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Practiced Roles</h3>
        <p className="text-gray-500">No interview data yet. Start your first interview to see your most practiced roles!</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Most Practiced Roles</h3>
      <div className="space-y-3">
        {roles.map((role, index) => (
          <div key={`${role.title}-${role.company}-${index}`} className="flex justify-between items-center">
            <div>
              <p className="font-medium text-gray-900">{role.title}</p>
              {role.company && <p className="text-sm text-gray-500">{role.company}</p>}
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

/**
 * Dashboard page with performance metrics (protected)
 */
export const Dashboard = () => {
  const { data: metrics, isLoading, isError } = useDashboardMetrics();

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" role="status" aria-label="Loading dashboard metrics"></div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="px-4 py-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Failed to load dashboard metrics
        </div>
      </div>
    );
  }

  if (!metrics || metrics.completed_interviews === 0) {
    return (
      <div className="px-4 py-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Performance Dashboard</h1>
        <div className="bg-white p-12 rounded-lg shadow text-center">
          <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Data Yet</h3>
          <p className="text-gray-600 mb-6">Complete your first interview to see your performance metrics here.</p>
          <a href="/browse-jobs" className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-md hover:bg-indigo-700 transition-colors">
            Browse Jobs
          </a>
        </div>
      </div>
    );
  }

  const avgScoreDisplay = metrics.average_score !== null
    ? metrics.average_score.toFixed(1)
    : 'N/A';

  return (
    <div className="px-4 py-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Performance Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <MetricCard
          title="Completed Interviews"
          value={metrics.completed_interviews}
        />
        <MetricCard
          title="Average Score"
          value={avgScoreDisplay}
          subtitle={metrics.average_score === null ? 'No feedback yet' : undefined}
        />
        <MetricCard
          title="Questions Answered"
          value={metrics.total_questions_answered}
        />
      </div>

      <MostPracticedRoles roles={metrics.most_practiced_roles} />
    </div>
  );
};

export default Dashboard;
