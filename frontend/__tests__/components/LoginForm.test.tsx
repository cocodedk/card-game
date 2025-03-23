import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/router';
import axios from 'axios';
import LoginForm from '../../src/components/LoginForm';
import * as authUtils from '../../src/utils/auth';

// Import the extended Jest matchers
import '@testing-library/jest-dom';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

// Mock auth utilities
jest.mock('../../src/utils/auth', () => ({
  storeTokens: jest.fn(),
  setAuthHeader: jest.fn(),
}));

describe('LoginForm', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    });
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';

    // Mock axios.isAxiosError
    (mockAxios as any).isAxiosError = jest.fn().mockReturnValue(true);
  });

  test('renders login form with all fields', () => {
    render(<LoginForm />);

    expect(screen.getByTestId('login-form')).toBeInTheDocument();
    expect(screen.getByTestId('username-input')).toBeInTheDocument();
    expect(screen.getByTestId('password-input')).toBeInTheDocument();
    expect(screen.getByTestId('remember-me-checkbox')).toBeInTheDocument();
    expect(screen.getByTestId('forgot-password-link')).toBeInTheDocument();
    expect(screen.getByTestId('login-button')).toBeInTheDocument();
    expect(screen.getAllByText('Sign In').length).toBeGreaterThan(0);
  });

  test('updates form values on input change', () => {
    render(<LoginForm />);

    const usernameInput = screen.getByTestId('username-input') as HTMLInputElement;
    const passwordInput = screen.getByTestId('password-input') as HTMLInputElement;

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    expect(usernameInput.value).toBe('testuser');
    expect(passwordInput.value).toBe('password123');
  });

  test('submits form and redirects on successful login', async () => {
    // Mock successful login response
    mockAxios.post.mockResolvedValueOnce({
      data: {
        tokens: {
          access: 'test-access-token',
          refresh: 'test-refresh-token'
        }
      }
    });

    render(<LoginForm />);

    // Fill form fields
    const usernameInput = screen.getByTestId('username-input');
    const passwordInput = screen.getByTestId('password-input');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    // Submit form
    const loginButton = screen.getByTestId('login-button');

    // Override preventDefault to ensure the form submission works
    const originalPreventDefault = Event.prototype.preventDefault;
    Event.prototype.preventDefault = jest.fn();
    fireEvent.click(loginButton);
    Event.prototype.preventDefault = originalPreventDefault;

    // Wait for API call to complete
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/players/login/',
        {
          username: 'testuser',
          password: 'password123',
        },
        { withCredentials: true }
      );
    });

    // Verify tokens were stored
    expect(authUtils.storeTokens).toHaveBeenCalledWith('test-access-token', 'test-refresh-token');
    expect(authUtils.setAuthHeader).toHaveBeenCalledWith('test-access-token');

    // Verify redirection to dashboard
    expect(mockPush).toHaveBeenCalledWith('/dashboard');
  });

  test('displays general error message on failed login', async () => {
    // Mock failed login response
    mockAxios.post.mockRejectedValueOnce({
      response: {
        data: {
          detail: 'Invalid credentials'
        }
      }
    });

    render(<LoginForm />);

    // Fill form fields
    const usernameInput = screen.getByTestId('username-input');
    const passwordInput = screen.getByTestId('password-input');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });

    // Submit form
    const loginButton = screen.getByTestId('login-button');

    // Override preventDefault
    const originalPreventDefault = Event.prototype.preventDefault;
    Event.prototype.preventDefault = jest.fn();
    fireEvent.click(loginButton);
    Event.prototype.preventDefault = originalPreventDefault;

    // Wait for error message to appear
    const errorMessage = await screen.findByTestId('login-error-general');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage.textContent).toBe('Invalid credentials');

    // Verify we didn't redirect
    expect(mockPush).not.toHaveBeenCalled();
  });

  test('handles 401 unauthorized error', async () => {
    // Mock 401 unauthorized response
    mockAxios.post.mockRejectedValueOnce({
      response: {
        status: 401,
        data: {}
      }
    });

    render(<LoginForm />);

    // Fill form fields and submit
    const usernameInput = screen.getByTestId('username-input');
    const passwordInput = screen.getByTestId('password-input');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });

    // Submit form
    const form = screen.getByTestId('login-form');

    // Override preventDefault
    const originalPreventDefault = Event.prototype.preventDefault;
    Event.prototype.preventDefault = jest.fn();
    fireEvent.submit(form);
    Event.prototype.preventDefault = originalPreventDefault;

    // Wait for error message
    const errorMessage = await screen.findByTestId('login-error-general');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage.textContent).toBe('Invalid username or password');
  });

  test('displays field-specific error messages', async () => {
    // Mock response with field errors
    mockAxios.post.mockRejectedValueOnce({
      response: {
        data: {
          username: ['This field is required'],
          password: ['This field cannot be blank']
        }
      }
    });

    render(<LoginForm />);

    // Submit form without filling fields
    const form = screen.getByTestId('login-form');

    // Override preventDefault
    const originalPreventDefault = Event.prototype.preventDefault;
    Event.prototype.preventDefault = jest.fn();
    fireEvent.submit(form);
    Event.prototype.preventDefault = originalPreventDefault;

    // Wait for error messages
    await waitFor(() => {
      expect(screen.getByTestId('username-error')).toBeInTheDocument();
      expect(screen.getByTestId('password-error')).toBeInTheDocument();
    });

    expect(screen.getByTestId('username-error').textContent).toBe('This field is required');
    expect(screen.getByTestId('password-error').textContent).toBe('This field cannot be blank');
  });

  test('displays generic error when non-Axios error occurs', async () => {
    // Mock a non-Axios error
    mockAxios.post.mockRejectedValueOnce(new Error('Network error'));
    (mockAxios as any).isAxiosError.mockReturnValueOnce(false);

    render(<LoginForm />);

    // Fill form fields
    const usernameInput = screen.getByTestId('username-input');
    const passwordInput = screen.getByTestId('password-input');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    // Submit form
    const form = screen.getByTestId('login-form');
    fireEvent.submit(form);

    // Wait for error message
    const errorMessage = await screen.findByTestId('login-error-general');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage.textContent).toBe('An error occurred during login. Please try again.');
  });

  test('shows loading state while submitting', async () => {
    // Create a promise that we can resolve manually
    let resolvePromise: (value: any) => void;
    const responsePromise = new Promise(resolve => {
      resolvePromise = resolve;
    });

    mockAxios.post.mockReturnValueOnce(responsePromise as any);

    render(<LoginForm />);

    // Fill form fields
    const usernameInput = screen.getByTestId('username-input');
    const passwordInput = screen.getByTestId('password-input');

    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    // Submit form
    const loginButton = screen.getByTestId('login-button');
    fireEvent.click(loginButton);

    // Check for loading state
    expect(screen.getByText('Signing in...')).toBeInTheDocument();
    expect(loginButton).toBeDisabled();

    // Resolve the promise to complete the test
    resolvePromise({
      data: {
        tokens: {
          access: 'test-access-token',
          refresh: 'test-refresh-token'
        }
      }
    });

    // Wait for the promise to resolve
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });
});
