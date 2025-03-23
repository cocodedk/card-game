import React from 'react';
import { render, screen, fireEvent, waitFor, within } from '@testing-library/react';
import { useRouter } from 'next/router';
import axios, { AxiosError } from 'axios';
import Dashboard from '../../src/pages/dashboard';
import * as auth from '../../src/utils/auth';

// Extend expect matchers
import '@testing-library/jest-dom';

// Mock the auth utils
jest.mock('../../src/utils/auth', () => ({
  isAuthenticated: jest.fn(),
  getAccessToken: jest.fn(),
  getRefreshToken: jest.fn(),
  clearTokens: jest.fn(),
  clearAuthHeader: jest.fn(),
}));

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

describe('Dashboard', () => {
  const mockPush = jest.fn();
  const mockPlayer = {
    username: 'testuser',
    callsign: 'Commander',
    email: 'test@example.com',
    first_name: 'Test',
    last_name: 'User',
    games_played: 10,
    wins: 7,
    losses: 3
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({
      push: mockPush
    });
    // Default to authenticated for most tests
    (auth.isAuthenticated as jest.Mock).mockReturnValue(true);
    (auth.getAccessToken as jest.Mock).mockReturnValue('mock-access-token');
    (auth.getRefreshToken as jest.Mock).mockReturnValue('mock-refresh-token');

    // Mock successful API response
    mockAxios.get.mockResolvedValue({ data: mockPlayer });

    // Mock axios.isAxiosError properly with a type predicate
    const originalIsAxiosError = axios.isAxiosError;
    (mockAxios as any).isAxiosError = function(payload: any): payload is AxiosError {
      return true;
    };
  });

  test('redirects to login if user is not authenticated', async () => {
    // Override the default mock to return false for this test
    (auth.isAuthenticated as jest.Mock).mockReturnValue(false);

    render(<Dashboard />);

    // Check if router.push was called with '/login'
    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  test('shows loading state initially', async () => {
    // Use fake timers to control setTimeout
    jest.useFakeTimers();

    // Delay the API response
    mockAxios.get.mockImplementation(() => new Promise(resolve => {
      setTimeout(() => resolve({ data: mockPlayer }), 100);
    }));

    render(<Dashboard />);

    // Check for loading spinner
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

    // Clean up timers
    jest.useRealTimers();
  });

  test('displays player profile data when loaded', async () => {
    render(<Dashboard />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText(/Welcome/)).toBeInTheDocument();
    });

    // Use within to scope searches to specific sections
    const profileSection = screen.getByTestId('profile-section');

    // Check profile information using more precise text matching
    expect(within(profileSection).getByText('Username:')).toBeInTheDocument();
    expect(within(profileSection).getByText('testuser')).toBeInTheDocument();
    expect(within(profileSection).getByText('Callsign:')).toBeInTheDocument();
    expect(within(profileSection).getByText('Commander')).toBeInTheDocument();
    expect(within(profileSection).getByText('Email:')).toBeInTheDocument();
    expect(within(profileSection).getByText('test@example.com')).toBeInTheDocument();

    // Look for the name paragraph directly
    const nameParagraphs = profileSection.querySelectorAll('p');
    let nameFound = false;

    // Test each paragraph to see if it contains the name information
    nameParagraphs.forEach(paragraph => {
      if (paragraph.textContent?.includes('Name:') &&
          paragraph.textContent?.includes('Test') &&
          paragraph.textContent?.includes('User')) {
        nameFound = true;
      }
    });

    // Verify we found the name paragraph
    expect(nameFound).toBe(true);
  });

  test('displays game statistics correctly', async () => {
    render(<Dashboard />);

    // Wait for data to load
    await waitFor(() => {
      expect(screen.getByText('Game Statistics')).toBeInTheDocument();
    });

    // Use within to scope searches to the stats section
    const statsSection = screen.getByTestId('stats-section');

    // Check stats by finding the label and value separately
    expect(within(statsSection).getByText('Games Played:')).toBeInTheDocument();
    expect(within(statsSection).getByText('10')).toBeInTheDocument();
    expect(within(statsSection).getByText('Wins:')).toBeInTheDocument();
    expect(within(statsSection).getByText('7')).toBeInTheDocument();
    expect(within(statsSection).getByText('Losses:')).toBeInTheDocument();
    expect(within(statsSection).getByText('3')).toBeInTheDocument();
    expect(within(statsSection).getByText('Win Rate:')).toBeInTheDocument();
    expect(within(statsSection).getByText('70.0%')).toBeInTheDocument();
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    mockAxios.get.mockRejectedValue({
      response: {
        status: 500,
        data: { detail: 'Server error' }
      }
    });

    render(<Dashboard />);

    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText(/Server error/)).toBeInTheDocument();
    });

    // Check for retry button
    expect(screen.getByText('Retry')).toBeInTheDocument();
  });

  test('handles 401 unauthorized errors by redirecting to login', async () => {
    // Use fake timers to control setTimeout
    jest.useFakeTimers();

    // Mock 401 error
    mockAxios.get.mockRejectedValue({
      response: {
        status: 401,
        data: { detail: 'Unauthorized' }
      }
    });

    render(<Dashboard />);

    // Wait for the clearTokens to be called
    await waitFor(() => {
      expect(auth.clearTokens).toHaveBeenCalled();
    });

    // Advance timers to trigger the setTimeout callback
    jest.advanceTimersByTime(200);

    // Check if router was called to redirect
    expect(mockPush).toHaveBeenCalledWith('/login');

    // Clean up timers
    jest.useRealTimers();
  });

  test('handles logout functionality', async () => {
    // Mock successful logout API response
    mockAxios.post.mockResolvedValue({ data: { success: true } });

    render(<Dashboard />);

    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByTestId('logout-button')).toBeInTheDocument();
    });

    // Click logout button
    fireEvent.click(screen.getByTestId('logout-button'));

    // Wait for API calls and cleanup actions
    await waitFor(() => {
      // Check if logout API was called
      expect(mockAxios.post).toHaveBeenCalledWith(
        expect.stringContaining('/api/players/logout/'),
        { refresh: 'mock-refresh-token' },
        expect.any(Object)
      );

      // Check if tokens were cleared
      expect(auth.clearTokens).toHaveBeenCalled();
      expect(auth.clearAuthHeader).toHaveBeenCalled();

      // Check if redirected to login
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  test('navigates to game creation page when Create Game is clicked', async () => {
    render(<Dashboard />);

    // Wait for dashboard to load
    await waitFor(() => {
      expect(screen.getByTestId('create-game-btn')).toBeInTheDocument();
    });

    // Click create game button
    fireEvent.click(screen.getByTestId('create-game-btn'));

    // Check if router pushed to game start page
    expect(mockPush).toHaveBeenCalledWith('/game/start');
  });
});
