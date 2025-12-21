/**
 * Authentication service for managing JWT tokens in localStorage.
 * Provides login, logout, and token management functions.
 *
 * @remarks
 * This service uses localStorage for token storage. Note that localStorage
 * is vulnerable to XSS attacks. Consider using httpOnly cookies for
 * production environments.
 */

const TOKEN_KEY = 'auth_token';

export const authService = {
  /**
   * Store JWT token in localStorage
   *
   * @param token - The JWT access token to store
   * @throws {Error} If localStorage is not available (e.g., in SSR context)
   * @example
   * authService.setToken('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...');
   */
  setToken(token: string): void {
    localStorage.setItem(TOKEN_KEY, token);
  },

  /**
   * Retrieve JWT token from localStorage
   *
   * @returns The stored JWT token, or null if no token exists
   * @throws {Error} If localStorage is not available
   * @example
   * const token = authService.getToken();
   * if (token) {
   *   // User is authenticated
   * }
   */
  getToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  /**
   * Check if user is authenticated (has valid token)
   *
   * @returns true if a token exists in localStorage, false otherwise
   * @remarks
   * This method only checks for token existence, not validity.
   * The token may be expired or invalid.
   * @example
   * if (authService.isAuthenticated()) {
   *   // Render authenticated UI
   * }
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  },

  /**
   * Logout user by removing token from localStorage
   *
   * @remarks
   * This is a client-side logout only. The JWT remains valid on the
   * server until expiration (stateless design).
   * @example
   * authService.logout();
   * navigate('/login');
   */
  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
  },

  /**
   * Login user by storing token
   *
   * @param token - The JWT access token received from login API
   * @throws {Error} If localStorage is not available
   * @example
   * const response = await loginApi(credentials);
   * authService.login(response.access_token);
   */
  login(token: string): void {
    this.setToken(token);
  },
};
