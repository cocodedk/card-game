/// <reference types="react" />
/// <reference types="react-dom" />
import React, { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/router';

// Add JSX namespace declaration to fix type errors
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

interface RegistrationFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName?: string;
  lastName?: string;
  dateOfBirth?: string;
  callsign?: string;
}

const PlayerRegistration: React.FC = () => {
  const router = useRouter();
  const [formData, setFormData] = useState<RegistrationFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    callsign: '',
  });

  const [errors, setErrors] = useState<Record<string, string | string[]>>({});
  const [success, setSuccess] = useState<string>('');
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
    setSuccess('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/players/register/`, {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        first_name: formData.firstName || undefined,
        last_name: formData.lastName || undefined,
        date_of_birth: formData.dateOfBirth || undefined,
        callsign: formData.callsign || undefined,
      }, {
        withCredentials: true
      });

      setSuccess('Registration successful! Redirecting to login...');
      // Reset form
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        firstName: '',
        lastName: '',
        dateOfBirth: '',
        callsign: '',
      });

      // Redirect to login page after a short delay
      setTimeout(() => {
        router.push('/login');
      }, 2000);

    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        const responseData = error.response.data;

        // Process API errors
        const processedErrors: Record<string, string | string[]> = {};

        // Handle non-field errors (often returned as 'detail' or 'non_field_errors')
        if (responseData.detail) {
          processedErrors.general = responseData.detail;
        }

        if (responseData.non_field_errors) {
          processedErrors.general = Array.isArray(responseData.non_field_errors)
            ? responseData.non_field_errors.join(', ')
            : responseData.non_field_errors;
        }

        // Map API field names to form field names
        const fieldMapping: Record<string, string> = {
          username: 'username',
          email: 'email',
          password: 'password',
          confirm_password: 'confirmPassword',
          first_name: 'firstName',
          last_name: 'lastName',
          date_of_birth: 'dateOfBirth',
          callsign: 'callsign'
        };

        // Process all field errors
        Object.entries(responseData).forEach(([key, value]) => {
          // Skip non-field errors already processed
          if (key !== 'detail' && key !== 'non_field_errors') {
            const formField = fieldMapping[key] || key;
            processedErrors[formField] = Array.isArray(value) ? value.join(', ') : String(value);
          }
        });

        setErrors(processedErrors);
      } else {
        setErrors({ general: 'An error occurred during registration. Please try again.' });
      }
      setIsLoading(false);
    }
  };

  // Helper function to display error messages
  const getErrorMessage = (fieldName: string): string => {
    const error = errors[fieldName];
    if (!error) return '';
    return Array.isArray(error) ? error.join(', ') : error;
  };

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 my-8">
      <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-white mb-6">Player Registration</h2>

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      )}

      {/* Display general errors at the top of the form */}
      {errors.general && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {getErrorMessage('general')}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="form-group">
          <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Username*
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
          {errors.username && <div className="text-red-500 text-sm mt-1">{getErrorMessage('username')}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="callsign" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Callsign/Pseudonym*
          </label>
          <input
            type="text"
            id="callsign"
            name="callsign"
            value={formData.callsign}
            onChange={handleChange}
            required
            className="input w-full"
            placeholder="Your in-game name"
          />
          {errors.callsign && <div className="text-red-500 text-sm mt-1">{getErrorMessage('callsign')}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Email*
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className="input w-full"
          />
          {errors.email && <div className="text-red-500 text-sm mt-1">{getErrorMessage('email')}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Password*
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
          {errors.password && <div className="text-red-500 text-sm mt-1">{getErrorMessage('password')}</div>}
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Confirm Password*
          </label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
            className="input w-full"
          />
          {errors.confirmPassword && <div className="text-red-500 text-sm mt-1">{getErrorMessage('confirmPassword')}</div>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="form-group">
            <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              First Name
            </label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleChange}
              className="input w-full"
            />
            {errors.firstName && <div className="text-red-500 text-sm mt-1">{getErrorMessage('firstName')}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Last Name
            </label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleChange}
              className="input w-full"
            />
            {errors.lastName && <div className="text-red-500 text-sm mt-1">{getErrorMessage('lastName')}</div>}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="dateOfBirth" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Date of Birth
          </label>
          <input
            type="date"
            id="dateOfBirth"
            name="dateOfBirth"
            value={formData.dateOfBirth}
            onChange={handleChange}
            className="input w-full"
          />
          {errors.dateOfBirth && <div className="text-red-500 text-sm mt-1">{getErrorMessage('dateOfBirth')}</div>}
        </div>

        <button
          type="submit"
          className="btn-primary w-full mt-6"
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Registering...
            </span>
          ) : (
            'Register'
          )}
        </button>
      </form>
    </div>
  );
};

export default PlayerRegistration;
