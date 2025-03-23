import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import PlayerInviteSection from '../../src/components/PlayerInviteSection';
import axios from 'axios';
import * as authUtils from '../../src/utils/auth';
import '@testing-library/jest-dom';

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

// Mock auth utilities
jest.mock('../../src/utils/auth', () => ({
  getAccessToken: jest.fn(),
}));

describe('PlayerInviteSection', () => {
  const mockOnInvitePlayer = jest.fn();
  const mockInvitedPlayers: { id: string; username: string; status: string }[] = [
    { id: 'player1', username: 'Player One', status: 'pending' },
    { id: 'player2', username: 'Player Two', status: 'accepted' },
    { id: 'player3', username: 'Player Three', status: 'declined' },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (authUtils.getAccessToken as jest.Mock).mockReturnValue('test-token');
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';

    // Mock the debounce timer
    jest.useFakeTimers();

    // Default axios mock implementation
    mockAxios.get.mockResolvedValue({
      data: [
        { user_uid: 'newplayer1', username: 'New Player 1', display_name: 'New Player 1' },
        { user_uid: 'newplayer2', username: 'New Player 2', display_name: 'New Player 2' },
      ]
    });
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('renders with invited players section when players are invited', () => {
    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    expect(screen.getByTestId('player-invite-section')).toBeInTheDocument();
    expect(screen.getByTestId('player-search-input')).toBeInTheDocument();
    expect(screen.getByTestId('search-button')).toBeInTheDocument();

    // Should show invited players section
    expect(screen.getByTestId('invited-players-section')).toBeInTheDocument();
    expect(screen.getByTestId('invited-player-0')).toBeInTheDocument();
    expect(screen.getByTestId('invited-player-1')).toBeInTheDocument();
    expect(screen.getByTestId('invited-player-2')).toBeInTheDocument();

    // Check player statuses
    expect(screen.getByTestId('player-status-0')).toHaveTextContent('Pending');
    expect(screen.getByTestId('player-status-1')).toHaveTextContent('Accepted');
    expect(screen.getByTestId('player-status-2')).toHaveTextContent('Declined');
  });

  test('shows warning when maximum players are reached', () => {
    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={4}
      />
    );

    // max is 4, current player + 3 invited = 4, so max is reached
    expect(screen.getByTestId('max-players-warning')).toBeInTheDocument();
    expect(screen.getByText('Maximum number of players reached. You cannot invite more players.')).toBeInTheDocument();

    // Search input should not be shown
    expect(screen.queryByTestId('player-search-input')).not.toBeInTheDocument();
  });

  test('performs search when input changes', async () => {
    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for the search results to appear
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalledWith(
        'http://localhost:8000/api/games/search/players/?query=test',
        { headers: { Authorization: 'Bearer test-token' } }
      );
    });

    // Should show search results
    await waitFor(() => {
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
    });

    expect(screen.getByTestId('search-result-0')).toBeInTheDocument();
    expect(screen.getByTestId('search-result-1')).toBeInTheDocument();
  });

  test('filters out already invited players from search results', async () => {
    // Mock search results including an already invited player
    mockAxios.get.mockResolvedValueOnce({
      data: [
        // Using a different format to match what the component expects
        { user_uid: 'player1', username: 'Player One', display_name: 'Invited Player One' },
        { user_uid: 'newplayer1', username: 'New Player 1', display_name: 'New Player 1' }
      ]
    });

    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'player' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for the search results to appear
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalled();
    });

    // Should only show the not-invited player
    await waitFor(() => {
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
    });

    // There should only be one search result
    expect(screen.queryByTestId('search-result-1')).not.toBeInTheDocument();
    expect(screen.getByTestId('search-result-0')).toHaveTextContent('New Player 1');

    // Check that there's no search result with "Invited Player One"
    const results = screen.getAllByTestId(/search-result-\d+/);
    expect(results.length).toBe(1);
    expect(results[0]).not.toHaveTextContent('Invited Player One');
  });

  test('invites player when invite button is clicked', async () => {
    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for the search results to appear
    await waitFor(() => {
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
    });

    // Click the invite button for the first result
    const inviteButton = screen.getByTestId('invite-button-0');
    fireEvent.click(inviteButton);

    expect(mockOnInvitePlayer).toHaveBeenCalledWith('newplayer1');
  });

  test('shows error message when search fails', async () => {
    // Mock a failed API call
    mockAxios.get.mockRejectedValueOnce(new Error('API error'));

    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByTestId('search-error')).toBeInTheDocument();
    });

    expect(screen.getByTestId('search-error')).toHaveTextContent('Failed to search players. Please try again.');
  });

  test('allows searching again after search fails', async () => {
    // First search fails
    mockAxios.get.mockRejectedValueOnce(new Error('API error'));

    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'fail' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByTestId('search-error')).toBeInTheDocument();
    });

    // Second search succeeds
    mockAxios.get.mockResolvedValueOnce({
      data: [{ user_uid: 'newplayer3', username: 'New Player 3', display_name: 'New Player 3' }]
    });

    // Search again
    fireEvent.change(searchInput, { target: { value: 'success' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for search results
    await waitFor(() => {
      expect(screen.getByTestId('search-results')).toBeInTheDocument();
    });

    // Error should be gone
    expect(screen.queryByTestId('search-error')).not.toBeInTheDocument();
  });

  test('handles empty search results', async () => {
    mockAxios.get.mockResolvedValueOnce({ data: [] });

    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'nonexistent' } });

    // Advance timers to trigger debounced search
    act(() => {
      jest.advanceTimersByTime(500);
    });

    // Wait for the search to complete
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalled();
    });

    // Should not show search results section
    expect(screen.queryByTestId('search-results')).not.toBeInTheDocument();
  });

  test('shows loading state in search button while searching', async () => {
    // Create a promise that we can resolve manually
    let resolvePromise: (value: any) => void;
    const responsePromise = new Promise(resolve => {
      resolvePromise = resolve;
    });

    mockAxios.get.mockReturnValueOnce(responsePromise as any);

    render(
      <PlayerInviteSection
        invitedPlayers={mockInvitedPlayers}
        onInvitePlayer={mockOnInvitePlayer}
        maxPlayers={6}
      />
    );

    // Click the search button instead of using debounce
    const searchInput = screen.getByTestId('player-search-input');
    fireEvent.change(searchInput, { target: { value: 'test' } });

    const searchButton = screen.getByTestId('search-button');
    fireEvent.click(searchButton);

    // Check for loading state
    expect(screen.getByText('...')).toBeInTheDocument();

    // Resolve the promise to complete the test
    resolvePromise!({
      data: [{ user_uid: 'newplayer1', username: 'New Player 1', display_name: 'New Player 1' }]
    });

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('...')).not.toBeInTheDocument();
    });
  });
});
