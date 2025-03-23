import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AIPlayerConfig from '../../src/components/AIPlayerConfig';
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

describe('AIPlayerConfig', () => {
  const mockGameId = 'game-123';

  beforeEach(() => {
    jest.clearAllMocks();
    (authUtils.getAccessToken as jest.Mock).mockReturnValue('test-token');
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';

    // Default axios mock implementation
    mockAxios.post.mockResolvedValue({
      data: {
        difficulty: 'medium'
      }
    });

    // Mock axios.isAxiosError
    (mockAxios as any).isAxiosError = jest.fn().mockReturnValue(true);
  });

  test('renders with max AI players information', () => {
    render(<AIPlayerConfig maxAIPlayers={3} gameId={mockGameId} />);

    expect(screen.getByTestId('ai-player-config')).toBeInTheDocument();
    expect(screen.getByTestId('ai-players-info')).toBeInTheDocument();
    expect(screen.getByText('You can add up to 3 AI players')).toBeInTheDocument();
    expect(screen.getByTestId('add-ai-button')).toBeInTheDocument();
  });

  test('shows warning when max players is reached (maxAIPlayers <= 0)', () => {
    render(<AIPlayerConfig maxAIPlayers={0} gameId={mockGameId} />);

    expect(screen.getByTestId('ai-max-players-warning')).toBeInTheDocument();
    expect(screen.getByText('Maximum number of players reached. You cannot add AI players.')).toBeInTheDocument();
    expect(screen.queryByTestId('add-ai-button')).not.toBeInTheDocument();
  });

  test('adds AI player when add button is clicked', async () => {
    // Override Date.now to return a fixed value for deterministic testing
    const originalDateNow = Date.now;
    Date.now = jest.fn(() => 1234567890);

    render(<AIPlayerConfig maxAIPlayers={3} gameId={mockGameId} />);

    const addButton = screen.getByTestId('add-ai-button');
    fireEvent.click(addButton);

    // Wait for the AI player to be added
    await waitFor(() => {
      expect(screen.getByTestId('ai-players-list')).toBeInTheDocument();
    });

    expect(screen.getByTestId('ai-player-0')).toBeInTheDocument();
    expect(screen.getByTestId('ai-difficulty-select-0')).toBeInTheDocument();
    expect(screen.getByTestId('remove-ai-button-0')).toBeInTheDocument();

    // Verify API call
    expect(mockAxios.post).toHaveBeenCalledWith(
      'http://localhost:8000/api/games/game-123/add_ai/',
      { difficulty: 'medium' },
      { headers: { Authorization: 'Bearer test-token' } }
    );

    // Verify difficulty info is shown
    expect(screen.getByTestId('difficulty-info')).toBeInTheDocument();
    expect(screen.getByText('Difficulty levels:')).toBeInTheDocument();

    // Restore original Date.now
    Date.now = originalDateNow;
  });

  test('shows error message when adding AI player fails', async () => {
    // Mock a failed API call
    mockAxios.post.mockRejectedValueOnce({
      response: {
        data: {
          error: 'Failed to create AI player'
        }
      }
    });

    render(<AIPlayerConfig maxAIPlayers={3} gameId={mockGameId} />);

    const addButton = screen.getByTestId('add-ai-button');
    fireEvent.click(addButton);

    // Wait for the error message to appear
    const errorMessage = await screen.findByTestId('ai-error-message');
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage.textContent).toContain('Failed to create AI player');

    // Verify no AI player was added
    expect(screen.queryByTestId('ai-players-list')).not.toBeInTheDocument();
  });

  test('removes AI player when remove button is clicked', async () => {
    // Override Date.now to return a fixed value for deterministic testing
    const originalDateNow = Date.now;
    Date.now = jest.fn(() => 1234567890);

    render(<AIPlayerConfig maxAIPlayers={3} gameId={mockGameId} />);

    // Add an AI player first
    const addButton = screen.getByTestId('add-ai-button');
    fireEvent.click(addButton);

    // Wait for the AI player to be added
    await waitFor(() => {
      expect(screen.getByTestId('ai-player-0')).toBeInTheDocument();
    });

    // Click the remove button
    const removeButton = screen.getByTestId('remove-ai-button-0');
    fireEvent.click(removeButton);

    // Verify the AI player was removed
    expect(screen.queryByTestId('ai-player-0')).not.toBeInTheDocument();
    expect(screen.queryByTestId('difficulty-info')).not.toBeInTheDocument();

    // Restore original Date.now
    Date.now = originalDateNow;
  });

  test('changes AI player difficulty when select is changed', async () => {
    // Override Date.now to return a fixed value for deterministic testing
    const originalDateNow = Date.now;
    Date.now = jest.fn(() => 1234567890);

    render(<AIPlayerConfig maxAIPlayers={3} gameId={mockGameId} />);

    // Add an AI player first
    const addButton = screen.getByTestId('add-ai-button');
    fireEvent.click(addButton);

    // Wait for the AI player to be added
    await waitFor(() => {
      expect(screen.getByTestId('ai-difficulty-select-0')).toBeInTheDocument();
    });

    // Change the difficulty
    const difficultySelect = screen.getByTestId('ai-difficulty-select-0');
    fireEvent.change(difficultySelect, { target: { value: 'hard' } });

    // Verify the difficulty was changed
    expect(difficultySelect).toHaveValue('hard');

    // Restore original Date.now
    Date.now = originalDateNow;
  });

  test('disables add button when max AI players are reached', async () => {
    render(<AIPlayerConfig maxAIPlayers={1} gameId={mockGameId} />);

    const addButton = screen.getByTestId('add-ai-button');
    fireEvent.click(addButton);

    // Wait for the AI player to be added
    await waitFor(() => {
      expect(screen.getByTestId('ai-player-0')).toBeInTheDocument();
    });

    // Verify the add button is disabled
    expect(addButton).toBeDisabled();
  });

  test('displays loading state in button when adding AI player', async () => {
    // Create a promise that we can resolve manually
    let resolvePromise: (value: any) => void;
    const responsePromise = new Promise(resolve => {
      resolvePromise = resolve;
    });

    mockAxios.post.mockReturnValueOnce(responsePromise as any);

    render(<AIPlayerConfig maxAIPlayers={3} gameId={mockGameId} />);

    const addButton = screen.getByTestId('add-ai-button');
    fireEvent.click(addButton);

    // Check for loading state
    expect(screen.getByText('Adding...')).toBeInTheDocument();

    // Resolve the promise to complete the test
    resolvePromise!({
      data: {
        difficulty: 'medium'
      }
    });

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Adding...')).not.toBeInTheDocument();
    });
  });
});
