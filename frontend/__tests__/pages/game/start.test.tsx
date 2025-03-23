import React from 'react';
import { render, screen, waitFor, fireEvent, within } from '@testing-library/react';
import GameStartPage from '../../../src/pages/game/start';
import * as auth from '../../../src/utils/auth';
import axios from 'axios';

// Set longer test timeouts for these async-heavy tests
jest.setTimeout(15000);

// Mock Next router
const mockPush = jest.fn();
jest.mock('next/router', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

// Mock axios
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

// Mock auth utility
jest.mock('../../../src/utils/auth', () => ({
  isAuthenticated: jest.fn(),
  getAccessToken: jest.fn(),
}));

// Mock components
jest.mock('../../../src/components/GameSetupForm', () => ({
  __esModule: true,
  default: ({ ruleSets, loadingRuleSets, onSettingsChange, onSubmit }: any) => {
    // Render the select with actual rule set options when available
    const selectContent = loadingRuleSets ? (
      <option>Loading...</option>
    ) : (
      ruleSets?.map((rule: any) => (
        <option key={rule.id} value={rule.id}>
          {rule.name}
        </option>
      ))
    );

    return (
      <div data-testid="game-setup-form">
        <select data-testid="rule-set-select">
          {loadingRuleSets ? <option>Loading...</option> : selectContent}
        </select>
        <input
          data-testid="max-players-input"
          type="number"
          value={4}
        />
        <label>
          <input
            data-testid="use-ai-checkbox"
            type="checkbox"
          />
          Use AI
        </label>
        <button
          data-testid="create-game-submit"
          onClick={() => {
            if (!loadingRuleSets) {
              onSubmit();
            }
          }}
        >
          {loadingRuleSets ? 'Loading Rule Sets...' : 'Create Game'}
        </button>
      </div>
    );
  },
}));

jest.mock('../../../src/components/PlayerInviteSection', () => ({
  __esModule: true,
  default: ({ invitedPlayers, onInvitePlayer, maxPlayers }: any) => (
    <div data-testid="player-invite-section">
      <input
        data-testid="invite-email-input"
        type="email"
        placeholder="Enter email to invite"
      />
      <button
        data-testid="invite-player-button"
        onClick={() => onInvitePlayer('test-player-id')}
      >
        Invite Player
      </button>
      <div data-testid="invited-players-list">
        {invitedPlayers.map((player: any) => (
          <div key={player.id} data-testid={`invited-player-${player.id}`}>
            {player.username} - {player.status}
          </div>
        ))}
      </div>
      <button data-testid="start-game-button">Start Game</button>
    </div>
  ),
}));

jest.mock('../../../src/components/AIPlayerConfig', () => ({
  __esModule: true,
  default: ({ maxAIPlayers, gameId }: any) => (
    <div data-testid="ai-player-config">
      <span>Max AI Players: {maxAIPlayers}</span>
      <span>Game ID: {gameId}</span>
    </div>
  ),
}));

describe('GameStartPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockPush.mockClear();

    // Mock authenticated user by default
    (auth.isAuthenticated as jest.Mock).mockReturnValue(true);
    (auth.getAccessToken as jest.Mock).mockReturnValue('test-token');

    // Mock rule sets response - resolve immediately to avoid timing issues
    mockAxios.get.mockImplementation((url) => {
      if (url.includes('/api/games/rule-sets/')) {
        return Promise.resolve({
          data: {
            rule_sets: [
              {
                id: 'rule-1',
                name: 'Standard Rules',
                description: 'Basic ruleset for the game',
                version: '1.0'
              }
            ]
          }
        });
      }
      return Promise.resolve({ data: {} });
    });

    // Mock successful game creation
    mockAxios.post.mockImplementation((url) => {
      if (url.includes('/api/games/') && !url.includes('/invite/') && !url.includes('/start/')) {
        return Promise.resolve({
          data: {
            game_uid: 'test-game-id'
          }
        });
      }

      if (url.includes('/invite/')) {
        return Promise.resolve({
          data: {
            username: 'Test Player',
            status: 'pending'
          }
        });
      }

      if (url.includes('/start/')) {
        return Promise.resolve({
          data: {
            started: true
          }
        });
      }
      return Promise.resolve({ data: {} });
    });
  });

  test('redirects to login if not authenticated', () => {
    // Mock user not authenticated
    (auth.isAuthenticated as jest.Mock).mockReturnValue(false);

    render(<GameStartPage />);

    // Router.push should be called with '/login'
    expect(mockPush).toHaveBeenCalledWith('/login');
  });

  test('fetches rule sets on mount', async () => {
    render(<GameStartPage />);

    // Should call the API to get rule sets
    expect(mockAxios.get).toHaveBeenCalled();
    const apiCallUrl = mockAxios.get.mock.calls[0][0];
    expect(apiCallUrl).toContain('/api/games/rule-sets/');

    // Form should exist
    const setupForm = await screen.findByTestId('game-setup-form');
    expect(setupForm).toBeInTheDocument();
  });

  test('renders correctly', async () => {
    render(<GameStartPage />);

    // Check for game settings section
    expect(screen.getByText('Game Settings')).toBeInTheDocument();

    // Check for form elements
    expect(screen.getByTestId('rule-set-select')).toBeInTheDocument();
    expect(screen.getByTestId('max-players-input')).toBeInTheDocument();
    expect(screen.getByTestId('use-ai-checkbox')).toBeInTheDocument();

    // We'll use getAllByTestId since there are multiple elements with the same test ID
    const createButtons = screen.getAllByTestId('create-game-submit');
    expect(createButtons.length).toBeGreaterThan(0);
  });

  test('creates a game when the create button is clicked', async () => {
    render(<GameStartPage />);

    // Wait for axios.get to have been called with the rule sets URL
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/games/rule-sets/'),
        expect.any(Object)
      );
    });

    // Force rule sets to be loaded by manipulating the component
    const createButtons = await screen.findAllByTestId('create-game-submit');
    expect(createButtons[0]).toHaveTextContent('Create Game');

    // Click the create button
    fireEvent.click(createButtons[0]);

    // Check if API was called
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalled();
    });

    // Wait for game ID to be displayed
    const gameId = await screen.findByTestId('game-id');
    expect(gameId).toBeInTheDocument();
    expect(gameId).toHaveTextContent('test-game-id');
  });

  test('displays error message when game creation fails', async () => {
    // Mock a failed game creation
    mockAxios.post.mockImplementationOnce(() => {
      return Promise.reject(new Error('Failed to create game'));
    });

    render(<GameStartPage />);

    // Wait for axios.get to have been called with the rule sets URL
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/games/rule-sets/'),
        expect.any(Object)
      );
    });

    // Force rule sets to be loaded by manipulating the component
    const createButtons = await screen.findAllByTestId('create-game-submit');
    expect(createButtons[0]).toHaveTextContent('Create Game');

    // Click the create button
    fireEvent.click(createButtons[0]);

    // Wait for error message to appear in the error container
    const errorMessage = await screen.findByTestId('game-error-message', {}, { timeout: 3000 });
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveTextContent('Failed to create game');
  });

  test('handles player invitation workflow', async () => {
    const { rerender } = render(<GameStartPage />);

    // Wait for axios.get to have been called with the rule sets URL
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/games/rule-sets/'),
        expect.any(Object)
      );
    });

    // Force rule sets to be loaded by manipulating the component
    const createButtons = await screen.findAllByTestId('create-game-submit');
    expect(createButtons[0]).toHaveTextContent('Create Game');

    // Click the create button
    fireEvent.click(createButtons[0]);

    // Wait for the game ID to appear, indicating game creation
    await screen.findByTestId('game-id', {}, { timeout: 3000 });

    // Force a rerender to reflect state changes
    rerender(<GameStartPage />);

    // Check if the invite section container is visible
    const inviteSectionContainer = await screen.findByTestId('invite-section-container', {}, { timeout: 3000 });
    expect(inviteSectionContainer).toBeInTheDocument();

    // Now we should have the player invite section
    const inviteSection = await screen.findByTestId('player-invite-section', {}, { timeout: 3000 });
    expect(inviteSection).toBeInTheDocument();

    // Find the email input and set a value
    const emailInput = within(inviteSection).getByTestId('invite-email-input');
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

    // Click the invite button
    const inviteButton = within(inviteSection).getByTestId('invite-player-button');
    fireEvent.click(inviteButton);

    // Check if API was called to invite player
    await waitFor(() => {
      // First call was createGame, second should be invitePlayer
      expect(mockAxios.post).toHaveBeenCalledTimes(2);
    });

    // Verify that the API call includes the player ID
    const secondCall = mockAxios.post.mock.calls[1];
    expect(secondCall[0]).toContain('/invite/');
    expect(secondCall[1]).toEqual({ player_uid: 'test-player-id' });

    // Wait for invited player to appear in list
    const invitedPlayer = await screen.findByTestId('invited-player-test-player-id', {}, { timeout: 3000 });
    expect(invitedPlayer).toBeInTheDocument();
    expect(invitedPlayer).toHaveTextContent('Test Player - pending');
  });

  test('shows AI configuration when enabled', async () => {
    render(<GameStartPage />);

    // Wait for axios.get to have been called with the rule sets URL
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/games/rule-sets/'),
        expect.any(Object)
      );
    });

    // Force rule sets to be loaded by manipulating the component
    const createButtons = await screen.findAllByTestId('create-game-submit');
    expect(createButtons[0]).toHaveTextContent('Create Game');

    // Toggle AI checkbox
    const aiCheckbox = screen.getByTestId('use-ai-checkbox');
    fireEvent.click(aiCheckbox);

    // Click the create button
    fireEvent.click(createButtons[0]);

    // Wait for the game ID to appear
    await screen.findByTestId('game-id', {}, { timeout: 3000 });

    // Check if AI section is visible
    const aiSection = await screen.findByTestId('ai-section-container');
    expect(aiSection).toBeInTheDocument();
  });

  test('starts the game and navigates to game page', async () => {
    render(<GameStartPage />);

    // Wait for axios.get to have been called with the rule sets URL
    await waitFor(() => {
      expect(mockAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('/api/games/rule-sets/'),
        expect.any(Object)
      );
    });

    // Force rule sets to be loaded by manipulating the component
    const createButtons = await screen.findAllByTestId('create-game-submit');
    expect(createButtons[0]).toHaveTextContent('Create Game');

    // Click the create button
    fireEvent.click(createButtons[0]);

    // Wait for the game ID to appear
    await screen.findByTestId('game-id', {}, { timeout: 3000 });

    // Wait for the start game button to appear
    const startButton = await screen.findByTestId('start-game-button', {}, { timeout: 3000 });
    expect(startButton).toBeInTheDocument();

    // Click the start game button
    fireEvent.click(startButton);

    // Check if the API was called to start the game
    await waitFor(() => {
      expect(mockAxios.post).toHaveBeenCalledTimes(2); // First call createGame, second startGame
    });

    // Verify the second API call is for starting the game
    const secondCall = mockAxios.post.mock.calls[1];
    expect(secondCall[0]).toContain('/start/');

    // Check if router was called to navigate to game page
    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/game/test-game-id');
    }, { timeout: 3000 });
  });
});
