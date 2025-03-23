import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PlayerSearch from '../../src/components/PlayerSearch';
import ApiService from '../../src/services/api';

// Mock the API service
jest.mock('../../src/services/api');

describe('PlayerSearch Component', () => {
  const mockOnSelectPlayer = jest.fn();
  const mockPlayers = [
    { id: 'player1', name: 'Player 1', status: 'online', ready: false },
    { id: 'player2', name: 'Player 2', status: 'offline', ready: false },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (ApiService.searchPlayers as jest.Mock).mockResolvedValue({
      data: { players: mockPlayers, total_count: 2 },
    });
  });

  it('renders search input', () => {
    render(<PlayerSearch onSelectPlayer={mockOnSelectPlayer} />);
    expect(screen.getByPlaceholderText('Search players...')).toBeInTheDocument();
  });

  it('shows loading state while searching', async () => {
    // Mock implementation with a delay to ensure loading state is visible
    (ApiService.searchPlayers as jest.Mock).mockImplementationOnce(() => {
      return new Promise(resolve => {
        setTimeout(() => {
          resolve({
            data: { players: mockPlayers, total_count: 2 },
          });
        }, 500);
      });
    });

    render(<PlayerSearch onSelectPlayer={mockOnSelectPlayer} />);

    fireEvent.change(screen.getByPlaceholderText('Search players...'), {
      target: { value: 'test' },
    });

    // Wait for the loading state to appear
    await waitFor(() => {
      expect(screen.getByText('Searching...')).toBeInTheDocument();
    });

    // Wait for the loading state to disappear
    await waitFor(() => {
      expect(screen.queryByText('Searching...')).not.toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('displays search results', async () => {
    render(<PlayerSearch onSelectPlayer={mockOnSelectPlayer} />);

    fireEvent.change(screen.getByPlaceholderText('Search players...'), {
      target: { value: 'test' },
    });

    await waitFor(() => {
      expect(screen.getByText('Player 1')).toBeInTheDocument();
      expect(screen.getByText('Player 2')).toBeInTheDocument();
    });
  });

  it('excludes specified player IDs from results', async () => {
    render(
      <PlayerSearch
        onSelectPlayer={mockOnSelectPlayer}
        excludePlayerIds={['player1']}
      />
    );

    fireEvent.change(screen.getByPlaceholderText('Search players...'), {
      target: { value: 'test' },
    });

    await waitFor(() => {
      expect(screen.queryByText('Player 1')).not.toBeInTheDocument();
      expect(screen.getByText('Player 2')).toBeInTheDocument();
    });
  });

  it('calls onSelectPlayer when a player is clicked', async () => {
    render(<PlayerSearch onSelectPlayer={mockOnSelectPlayer} />);

    fireEvent.change(screen.getByPlaceholderText('Search players...'), {
      target: { value: 'test' },
    });

    await waitFor(() => {
      fireEvent.click(screen.getByText('Player 1'));
    });

    expect(mockOnSelectPlayer).toHaveBeenCalledWith(mockPlayers[0]);
  });

  it('shows error message when API call fails', async () => {
    const errorMessage = 'Failed to search players';
    (ApiService.searchPlayers as jest.Mock).mockRejectedValueOnce(new Error(errorMessage));

    render(<PlayerSearch onSelectPlayer={mockOnSelectPlayer} />);

    fireEvent.change(screen.getByPlaceholderText('Search players...'), {
      target: { value: 'test' },
    });

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('shows no results message when search returns empty', async () => {
    (ApiService.searchPlayers as jest.Mock).mockResolvedValueOnce({
      data: { players: [], total_count: 0 },
    });

    render(<PlayerSearch onSelectPlayer={mockOnSelectPlayer} />);

    fireEvent.change(screen.getByPlaceholderText('Search players...'), {
      target: { value: 'nonexistent' },
    });

    await waitFor(() => {
      expect(screen.getByText('No players found')).toBeInTheDocument();
    });
  });
});
