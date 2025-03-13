/// <reference types="react" />
/// <reference types="react-dom" />
import React, { useState } from 'react';
import axios from 'axios';

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

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState<string>('');

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

    try {
      const response = await axios.post('/api/players/register/', {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        first_name: formData.firstName || undefined,
        last_name: formData.lastName || undefined,
        date_of_birth: formData.dateOfBirth || undefined,
        callsign: formData.callsign || undefined,
      });

      setSuccess('Registration successful!');
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

    } catch (error) {
      if (axios.isAxiosError(error) && error.response) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'An error occurred during registration' });
      }
    }
  };

  return (
    <div className="max-w-md mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 my-8">
      <h2 className="text-2xl font-bold text-center text-gray-800 dark:text-white mb-6">Player Registration</h2>

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {success}
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
          {errors.username && <div className="text-red-500 text-sm mt-1">{errors.username}</div>}
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
          {errors.callsign && <div className="text-red-500 text-sm mt-1">{errors.callsign}</div>}
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
          {errors.email && <div className="text-red-500 text-sm mt-1">{errors.email}</div>}
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
          {errors.password && <div className="text-red-500 text-sm mt-1">{errors.password}</div>}
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
          {errors.confirm_password && <div className="text-red-500 text-sm mt-1">{errors.confirm_password}</div>}
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
        </div>

        {errors.general && <div className="text-red-500 text-sm mt-1">{errors.general}</div>}

        <button type="submit" className="btn-primary w-full mt-6">Register</button>
      </form>
    </div>
  );
};

export default PlayerRegistration;
