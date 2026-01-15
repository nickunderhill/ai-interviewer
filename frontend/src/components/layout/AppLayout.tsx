/**
 * App layout with navigation and logout button
 */
import { useAuth } from '../../features/auth/hooks/useAuth';
import { Outlet, Link } from 'react-router-dom';
import { LanguageSwitcher } from '../common/LanguageSwitcher';
import { useTranslation } from 'react-i18next';

const AppLayout = () => {
  const { logout } = useAuth();
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link
                to="/dashboard"
                className="text-xl font-bold text-gray-900 hover:text-indigo-600 transition-colors"
              >
                {t('app.title')}
              </Link>
              <div className="flex space-x-4">
                <Link
                  to="/dashboard"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  {t('nav.dashboard')}
                </Link>
                <Link
                  to="/history"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  {t('nav.history')}
                </Link>
                <Link
                  to="/progress"
                  className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
                >
                  {t('nav.progress')}
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <LanguageSwitcher />
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                {t('nav.logout')}
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
};

export default AppLayout;
