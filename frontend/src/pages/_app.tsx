import '@/styles/globals.css';
import type { AppProps } from 'next/app';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useEffect } from 'react';
import axios from 'axios';
import { getAccessToken, getRefreshToken, storeTokens, clearTokens, setAuthHeader } from '../utils/auth';

// Create a client
const queryClient = new QueryClient();

export default function App({ Component, pageProps }: AppProps) {
  // Configure axios defaults
  useEffect(() => {
    // Set withCredentials globally for all axios requests
    axios.defaults.withCredentials = true;

    // Check for stored tokens and set authorization header if they exist
    const accessToken = getAccessToken();
    if (accessToken) {
      setAuthHeader(accessToken);
    }

    // Add request interceptor to handle authentication
    axios.interceptors.request.use(
      (config) => {
        // Get the token on each request in case it was updated
        const token = getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor to handle common errors
    axios.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // If the error is 401 and we have a refresh token, try to get a new access token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = getRefreshToken();
            if (refreshToken) {
              try {
                const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/players/token/refresh/`, {
                  refresh: refreshToken
                });

                if (response.data.access) {
                  // Store the new access token
                  storeTokens(response.data.access, refreshToken);
                  setAuthHeader(response.data.access);
                  originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

                  // Retry the original request
                  return axios(originalRequest);
                }
              } catch (refreshError) {
                console.error('Error refreshing token:', refreshError);

                // Handle different refresh error scenarios
                if (axios.isAxiosError(refreshError)) {
                  if (refreshError.response?.status === 401) {
                    // Invalid refresh token
                    console.log('Refresh token invalid or expired');
                  } else if (refreshError.response?.status === 500) {
                    // Server error
                    console.error('Server error during token refresh:', refreshError.response?.data);
                  }
                }

                // If refresh fails, clear tokens and redirect to login
                if (typeof window !== 'undefined') {
                  clearTokens();
                  window.location.href = '/login';
                }
              }
            } else {
              // No refresh token available
              if (typeof window !== 'undefined') {
                window.location.href = '/login';
              }
            }
          } catch (error) {
            console.error('Error in refresh token process:', error);
            // If refresh fails, redirect to login
            if (typeof window !== 'undefined') {
              clearTokens();
              window.location.href = '/login';
            }
          }
        } else if (error.response?.status === 500) {
          // Handle server errors
          console.error('Server error:', error.response?.data);
        }

        // Log errors in development
        if (process.env.NODE_ENV === 'development') {
          console.error('Axios error:', error);
        }

        return Promise.reject(error);
      }
    );
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <Component {...pageProps} />
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  );
}
