// Authentication utility functions

/**
 * Store authentication tokens in localStorage
 */
export const storeTokens = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem('accessToken', accessToken);
  localStorage.setItem('refreshToken', refreshToken);
};

/**
 * Get the access token from localStorage
 */
export const getAccessToken = (): string | null => {
  return localStorage.getItem('accessToken');
};

/**
 * Get the refresh token from localStorage
 */
export const getRefreshToken = (): string | null => {
  return localStorage.getItem('refreshToken');
};

/**
 * Clear authentication tokens from localStorage
 */
export const clearTokens = (): void => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
};

/**
 * Check if the user is authenticated (has an access token)
 */
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

/**
 * Set the Authorization header for axios
 */
export const setAuthHeader = (token: string): void => {
  if (typeof window !== 'undefined') {
    // Only run on client side
    const axios = require('axios').default;
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
};

/**
 * Clear the Authorization header for axios
 */
export const clearAuthHeader = (): void => {
  if (typeof window !== 'undefined') {
    // Only run on client side
    const axios = require('axios').default;
    delete axios.defaults.headers.common['Authorization'];
  }
};

/**
 * Handle logout - clear tokens and headers
 */
export const logout = (): void => {
  clearTokens();
  clearAuthHeader();
};
