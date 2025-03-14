import React, { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';
import { storeTokens, setAuthHeader } from '../utils/auth';

const LoginForm: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/players/login/`, {
        username: formData.username,
        password: formData.password,
      }, {
        withCredentials: true
      });

      // Store tokens in localStorage and set auth header
      if (response.data.tokens) {
        const { access, refresh } = response.data.tokens;
        storeTokens(access, refresh);
        setAuthHeader(access);
      }

      // Redirect to dashboard or game page on successful login
      router.push('/dashboard');
    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        const responseData = error.response.data;
        const processedErrors: Record<string, string> = {};

        // Handle non-field errors (often returned as 'detail' or 'non_field_errors')
        if (responseData.detail) {
          processedErrors.general = responseData.detail;
        } else if (responseData.non_field_errors) {
          processedErrors.general = Array.isArray(responseData.non_field_errors)
            ? responseData.non_field_errors.join(', ')
            : responseData.non_field_errors;
        } else if (error.response.status === 401) {
          // Handle 401 Unauthorized errors
          processedErrors.general = 'Invalid username or password';
        }

        // Process all field errors
        Object.entries(responseData).forEach(([key, value]) => {
          // Skip non-field errors already processed
          if (key !== 'detail' && key !== 'non_field_errors') {
            processedErrors[key] = Array.isArray(value) ? value.join(', ') : String(value);
          }
        });

        // If no specific errors were found, add a generic error
        if (Object.keys(processedErrors).length === 0) {
          processedErrors.general = 'Login failed. Please check your credentials and try again.';
        }

        setErrors(processedErrors);
      } else {
        setErrors({ general: 'An error occurred during login. Please try again.' });
      }
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 my-8">
      <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-white mb-6">Sign In</h2>

      {/* Display general errors at the top of the form */}
      {errors.general && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {errors.general}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="form-group">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Username
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
            className="input w-full"
          />
          {errors.username && <div className="text-red-500 text-sm mt-1">{errors.username}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Password
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
            className="input w-full"
          />
          {errors.password && <div className="text-red-500 text-sm mt-1">{errors.password}</div>}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="checkbox"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Remember me
            </label>
          </div>

          <div className="text-sm">
            <a href="#" className="text-primary-600 hover:text-primary-500">
              Forgot your password?
            </a>
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary w-full"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Signing in...
            </span>
          ) : (
            'Sign In'
          )}
        </button>
      </form>
    </div>
  );
};

export default LoginForm;
