/**
 * Registration form component with validation
 */
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useAuth } from '../hooks/useAuth';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from '../../../components/common/LanguageSwitcher';

type RegisterFormData = {
  email: string;
  password: string;
  confirmPassword: string;
};

const RegisterForm = () => {
  const { register: registerUser, isLoading, error } = useAuth();
  const { t } = useTranslation();

  const registerSchema = z
    .object({
      email: z.string().email(t('auth.validation.emailInvalid')),
      password: z
        .string()
        .min(8, t('auth.validation.passwordMin'))
        .max(128, t('auth.validation.passwordMax')),
      confirmPassword: z.string(),
    })
    .refine(data => data.password === data.confirmPassword, {
      message: t('auth.register.passwordMismatch'),
      path: ['confirmPassword'],
    });
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data: RegisterFormData) => {
    registerUser({ email: data.email, password: data.password });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <div className="flex justify-end mb-4">
          <LanguageSwitcher />
        </div>
        <div>
          <h2 className="text-center text-3xl font-bold text-gray-900">
            {t('auth.register.title')}
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {t('auth.register.error')}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                {t('auth.register.email')}
              </label>
              <input
                id="email"
                type="email"
                {...register('email')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.email.message}
                </p>
              )}
            </div>
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700"
              >
                {t('auth.register.password')}
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                {...register('password')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.password.message}
                </p>
              )}
            </div>
            <div>
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-medium text-gray-700"
              >
                {t('auth.register.confirmPassword')}
              </label>
              <input
                id="confirmPassword"
                type="password"
                autoComplete="new-password"
                {...register('confirmPassword')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>
          </div>
          <div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400"
            >
              {isLoading
                ? t('auth.register.submitting')
                : t('auth.register.submit')}
            </button>
          </div>
          <div className="text-center">
            <Link
              to="/login"
              className="text-sm text-indigo-600 hover:text-indigo-500"
            >
              {t('auth.register.loginLink')}
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterForm;
