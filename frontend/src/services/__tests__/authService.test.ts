/**
 * Unit tests for authService
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { authService } from '../authService';

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  describe('setToken', () => {
    it('should store token in localStorage', () => {
      const token = 'test-jwt-token';
      authService.setToken(token);
      expect(localStorage.getItem('auth_token')).toBe(token);
    });
  });

  describe('getToken', () => {
    it('should retrieve token from localStorage', () => {
      const token = 'test-jwt-token';
      localStorage.setItem('auth_token', token);
      expect(authService.getToken()).toBe(token);
    });

    it('should return null when no token exists', () => {
      expect(authService.getToken()).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when token exists', () => {
      localStorage.setItem('auth_token', 'test-token');
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('should return false when no token exists', () => {
      expect(authService.isAuthenticated()).toBe(false);
    });
  });

  describe('logout', () => {
    it('should remove token from localStorage', () => {
      localStorage.setItem('auth_token', 'test-token');
      authService.logout();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('login', () => {
    it('should store token from response', () => {
      const token = 'new-jwt-token';
      authService.login(token);
      expect(localStorage.getItem('auth_token')).toBe('new-jwt-token');
    });
  });
});
