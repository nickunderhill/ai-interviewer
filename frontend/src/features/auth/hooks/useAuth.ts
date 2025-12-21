/**
 * Custom hook for authentication state and actions
 */
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import { authService } from '../../../services/authService';
import { authApi } from '../api';
import type { LoginRequest, RegisterRequest } from '../types/auth';

export const useAuth = () => {
  const navigate = useNavigate();

  const loginMutation = useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: data => {
      authService.login(data.access_token);
      navigate('/dashboard');
    },
  });

  const registerMutation = useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: () => {
      navigate('/login');
    },
  });

  const logout = () => {
    authService.logout();
    navigate('/login');
  };

  // Cache isAuthenticated to avoid unnecessary localStorage reads on every render
  const isAuthenticated = useMemo(() => authService.isAuthenticated(), []);

  return {
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout,
    isLoading: loginMutation.isPending || registerMutation.isPending,
    error: loginMutation.error || registerMutation.error,
    isAuthenticated,
  };
};
