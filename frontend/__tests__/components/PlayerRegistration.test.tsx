import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import PlayerRegistration from '../../src/components/PlayerRegistration';
import axios from 'axios';
import '@testing-library/jest-dom';

// Mock Next.js router
const mockPush = jest.fn();
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

describe('PlayerRegistration', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    // Reset mock implementation
    mockAxios.post.mockReset();

    // Mock axios.isAxiosError
    (mockAxios as any).isAxiosError = jest.fn().mockReturnValue(true);

    // Set environment variable
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';

    // Mock successful registration by default
    mockAxios.post.mockResolvedValue({ data: { message: 'Registration successful' } });

    // Mock timers
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('renders the registration form with all fields', () => {
    render(<PlayerRegistration />);

    // Check if the form and title are rendered
    expect(screen.getByTestId('registration-form')).toBeInTheDocument();
    expect(screen.getByText('Player Registration')).toBeInTheDocument();

    // Check all required input fields
    expect(screen.getByTestId('username-input')).toBeInTheDocument();
    expect(screen.getByTestId('callsign-input')).toBeInTheDocument();
    expect(screen.getByTestId('email-input')).toBeInTheDocument();
    expect(screen.getByTestId('password-input')).toBeInTheDocument();
    expect(screen.getByTestId('confirm-password-input')).toBeInTheDocument();

    // Check optional fields
    expect(screen.getByTestId('first-name-input')).toBeInTheDocument();
    expect(screen.getByTestId('last-name-input')).toBeInTheDocument();
    expect(screen.getByTestId('date-of-birth-input')).toBeInTheDocument();

    // Check submit button
    expect(screen.getByTestId('register-button')).toBeInTheDocument();
  });

  test('allows input in all fields and updates form data', () => {
    render(<PlayerRegistration />);

    // Get all input fields
    const usernameInput = screen.getByTestId('username-input');
    const callsignInput = screen.getByTestId('callsign-input');
    const emailInput = screen.getByTestId('email-input');
    const passwordInput = screen.getByTestId('password-input');
    const confirmPasswordInput = screen.getByTestId('confirm-password-input');
    const firstNameInput = screen.getByTestId('first-name-input');
    const lastNameInput = screen.getByTestId('last-name-input');
    const dateOfBirthInput = screen.getByTestId('date-of-birth-input');

    // Enter values in each field
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.change(callsignInput, { target: { value: 'TestPlayer' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'Password123!' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'Password123!' } });
    fireEvent.change(firstNameInput, { target: { value: 'Test' } });
    fireEvent.change(lastNameInput, { target: { value: 'User' } });
    fireEvent.change(dateOfBirthInput, { target: { value: '1990-01-01' } });

    // Check if values are updated
    expect(usernameInput).toHaveValue('testuser');
    expect(callsignInput).toHaveValue('TestPlayer');
    expect(emailInput).toHaveValue('test@example.com');
    expect(passwordInput).toHaveValue('Password123!');
    expect(confirmPasswordInput).toHaveValue('Password123!');
    expect(firstNameInput).toHaveValue('Test');
    expect(lastNameInput).toHaveValue('User');
    expect(dateOfBirthInput).toHaveValue('1990-01-01');
  });

  test('handles successful registration and redirects to login', async () => {
    render(<PlayerRegistration />);

    // Fill out the form
    fireEvent.change(screen.getByTestId('username-input'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByTestId('callsign-input'), { target: { value: 'TestPlayer' } });
    fireEvent.change(screen.getByTestId('email-input'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByTestId('password-input'), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByTestId('confirm-password-input'), { target: { value: 'Password123!' } });

    // Submit the form
    fireEvent.click(screen.getByTestId('register-button'));

    // Check if API call was made with correct data
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledWith(
        'http://localhost:8000/api/players/register/',
        {
          username: 'testuser',
          email: 'test@example.com',
          password: 'Password123!',
          confirm_password: 'Password123!',
          first_name: undefined,
          last_name: undefined,
          date_of_birth: undefined,
          callsign: 'TestPlayer',
        },
        { withCredentials: true }
      );
    });

    // Check for success message
    const successMessage = await screen.findByTestId('success-message');
    expect(successMessage).toBeInTheDocument();
    expect(successMessage).toHaveTextContent('Registration successful! Redirecting to login...');

    // Fast-forward timers to trigger redirect
    jest.advanceTimersByTime(2000);

    // Check if redirect to login happens
    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  test('displays general error when registration fails', async () => {
    // Mock API to return error
    mockAxios.post.mockRejectedValueOnce({
      response: {
        data: {
          non_field_errors: ['Registration failed due to server error']
        }
      }
    });

    render(<PlayerRegistration />);

    // Fill out the form
    fireEvent.change(screen.getByTestId('username-input'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByTestId('callsign-input'), { target: { value: 'TestPlayer' } });
    fireEvent.change(screen.getByTestId('email-input'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByTestId('password-input'), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByTestId('confirm-password-input'), { target: { value: 'Password123!' } });

    // Submit the form
    fireEvent.click(screen.getByTestId('register-button'));

    // Check for error message
    const errorMessage = await screen.findByTestId('general-error');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveTextContent('Registration failed due to server error');

    // Should not redirect
    expect(mockPush).not.toHaveBeenCalled();
  });

  test('displays field-specific errors', async () => {
    // Mock API to return field errors
    mockAxios.post.mockRejectedValueOnce({
      response: {
        data: {
          username: ['Username already exists'],
          email: ['Invalid email format'],
          password: ['Password is too weak'],
          confirm_password: ['Passwords do not match']
        }
      }
    });

    render(<PlayerRegistration />);

    // Fill out the form
    fireEvent.change(screen.getByTestId('username-input'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByTestId('callsign-input'), { target: { value: 'TestPlayer' } });
    fireEvent.change(screen.getByTestId('email-input'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByTestId('password-input'), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByTestId('confirm-password-input'), { target: { value: 'DifferentPassword!' } });

    // Submit the form
    fireEvent.click(screen.getByTestId('register-button'));

    // Check for field-specific error messages
    await waitFor(() => {
      expect(screen.getByTestId('username-error')).toBeInTheDocument();
      expect(screen.getByTestId('email-error')).toBeInTheDocument();
      expect(screen.getByTestId('password-error')).toBeInTheDocument();
      expect(screen.getByTestId('confirm-password-error')).toBeInTheDocument();
    });

    expect(screen.getByTestId('username-error')).toHaveTextContent('Username already exists');
    expect(screen.getByTestId('email-error')).toHaveTextContent('Invalid email format');
    expect(screen.getByTestId('password-error')).toHaveTextContent('Password is too weak');
    expect(screen.getByTestId('confirm-password-error')).toHaveTextContent('Passwords do not match');
  });

  test('displays loading state while submitting the form', async () => {
    // Create a promise that we can resolve manually
    let resolvePromise: (value: any) => void;
    const responsePromise = new Promise(resolve => {
      resolvePromise = resolve;
    });

    mockAxios.post.mockReturnValueOnce(responsePromise as any);

    render(<PlayerRegistration />);

    // Fill out the form
    fireEvent.change(screen.getByTestId('username-input'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByTestId('callsign-input'), { target: { value: 'TestPlayer' } });
    fireEvent.change(screen.getByTestId('email-input'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByTestId('password-input'), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByTestId('confirm-password-input'), { target: { value: 'Password123!' } });

    // Submit the form
    fireEvent.click(screen.getByTestId('register-button'));

    // Check for loading text
    expect(screen.getByText('Registering...')).toBeInTheDocument();

    // Resolve the promise
    resolvePromise!({ data: { message: 'Registration successful' } });

    // Wait for success message to appear
    await waitFor(() => {
      expect(screen.getByTestId('success-message')).toBeInTheDocument();
    });

    // Success message should contain the expected text
    expect(screen.getByTestId('success-message')).toHaveTextContent('Registration successful! Redirecting to login...');
  });

  test('handles non-axios errors gracefully', async () => {
    // Mock a generic error
    (mockAxios as any).isAxiosError.mockReturnValueOnce(false);
    mockAxios.post.mockRejectedValueOnce(new Error('Unknown error'));

    render(<PlayerRegistration />);

    // Fill out the form
    fireEvent.change(screen.getByTestId('username-input'), { target: { value: 'testuser' } });
    fireEvent.change(screen.getByTestId('callsign-input'), { target: { value: 'TestPlayer' } });
    fireEvent.change(screen.getByTestId('email-input'), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByTestId('password-input'), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByTestId('confirm-password-input'), { target: { value: 'Password123!' } });

    // Submit the form
    fireEvent.click(screen.getByTestId('register-button'));

    // Check for generic error message
    const errorMessage = await screen.findByTestId('general-error');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveTextContent('An error occurred during registration. Please try again.');
  });
});
