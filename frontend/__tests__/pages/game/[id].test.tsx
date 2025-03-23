import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/router';
import axios from 'axios';
import GamePage from '@/pages/game/[id]';
import { GameState, Player, Card } from '@/types/game';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock WebSocket
class MockWebSocket {
  onmessage: ((event: MessageEvent) => void) | null = null;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  send = jest.fn();
  close = jest.fn();
}

// Mock global WebSocket
global.WebSocket = MockWebSocket as any;

describe('Game Page', () => {
  const mockRouter = {
    query: { id: 'game-123' },
    push: jest.fn(),
  };

  const mockPlayer: Player = {
    id: 'player-1',
    name: 'Test Player',
    avatarUrl: '/avatar.png',
  };

  const mockPlayers: Player[] = [
    mockPlayer,
    {
      id: 'player-2',
      name: 'Opponent',
      avatarUrl: '/avatar2.png',
    },
  ];

  const mockGameState: GameState = {
    id: 'game-123',
    status: 'in_progress',
    currentPlayer: 'player-1',
    nextPlayer: 'player-2',
    direction: 'clockwise',
    discardPile: [{ id: 'card-1', suit: 'hearts', value: '7', color: 'red' }],
    currentSuit: 'hearts',
    deck: [],
    playerStates: {
      'player-1': {
        hand: [
          { id: 'card-2', suit: 'hearts', value: '8', color: 'red' },
          { id: 'card-3', suit: 'diamonds', value: '5', color: 'red' },
        ],
        announcedOneCard: false,
        penalties: 0,
      },
      'player-2': {
        hand: [],
        announcedOneCard: false,
        penalties: 0,
      },
    },
    winnerId: null,
    gameOver: false,
  };

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue(mockRouter);

    // Mock API responses
    mockedAxios.get.mockResolvedValueOnce({
      data: {
        game: {
          id: 'game-123',
          status: 'in_progress',
        },
        players: mockPlayers,
        currentPlayerId: 'player-1',
      },
    });

    localStorage.setItem('userToken', 'test-token');
    localStorage.setItem('playerId', 'player-1');
  });

  afterEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('loads and displays the game page', async () => {
    render(<GamePage />);

    // Check loading state
    expect(screen.getByTestId('loading-game')).toBeInTheDocument();

    // Mock WebSocket connection and message
    const mockWs = new MockWebSocket();
    // Simulate connection open and message with game state
    if (mockWs.onopen) {
      mockWs.onopen(new Event('open'));
    }

    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: mockGameState,
        }),
      }));
    }

    // Wait for game board to appear
    await waitFor(() => {
      expect(screen.queryByTestId('loading-game')).not.toBeInTheDocument();
      expect(screen.getByTestId('game-board')).toBeInTheDocument();
    });

    // Check game status elements
    expect(screen.getByTestId('game-status')).toHaveTextContent('Current Turn: Test Player');
    expect(screen.getByTestId('game-status')).toHaveTextContent('Next Turn: Opponent');
    expect(screen.getByTestId('game-status')).toHaveTextContent('Direction: Clockwise');

    // Check discard pile
    expect(screen.getByTestId('discard-pile')).toBeInTheDocument();
    expect(screen.getByTestId('discard-value')).toHaveTextContent('7');

    // Check player's hand is displayed
    expect(screen.getByTestId('player-hand')).toBeInTheDocument();
    expect(screen.getAllByTestId('card')).toHaveLength(2);
  });

  test('handles playing a card', async () => {
    render(<GamePage />);

    // Mock WebSocket connection and message
    const mockWs = new MockWebSocket();
    if (mockWs.onopen) {
      mockWs.onopen(new Event('open'));
    }

    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: mockGameState,
        }),
      }));
    }

    // Wait for game board to appear
    await waitFor(() => {
      expect(screen.getByTestId('game-board')).toBeInTheDocument();
    });

    // Play a card
    const cards = screen.getAllByTestId('card');
    fireEvent.click(cards[0]);

    // Check that WebSocket message was sent
    expect(mockWs.send).toHaveBeenCalledWith(
      expect.stringContaining('"type":"play_card"')
    );

    // Simulate updated game state after playing card
    const updatedGameState = {
      ...mockGameState,
      playerStates: {
        ...mockGameState.playerStates,
        'player-1': {
          ...mockGameState.playerStates['player-1'],
          hand: [{ id: 'card-3', suit: 'diamonds', value: '5', color: 'red' }],
        },
      },
      discardPile: [
        { id: 'card-2', suit: 'hearts', value: '8', color: 'red' },
        ...mockGameState.discardPile,
      ],
    };

    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: updatedGameState,
        }),
      }));
    }

    // Check that the player's hand is updated
    await waitFor(() => {
      expect(screen.getAllByTestId('card')).toHaveLength(1);
    });
  });

  test('handles drawing a card', async () => {
    render(<GamePage />);

    // Mock WebSocket connection and message
    const mockWs = new MockWebSocket();
    if (mockWs.onopen) {
      mockWs.onopen(new Event('open'));
    }

    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: mockGameState,
        }),
      }));
    }

    // Wait for game board to appear
    await waitFor(() => {
      expect(screen.getByTestId('game-board')).toBeInTheDocument();
    });

    // Click the draw card button
    const drawButton = screen.getByTestId('draw-card-button');
    fireEvent.click(drawButton);

    // Check that WebSocket message was sent
    expect(mockWs.send).toHaveBeenCalledWith(
      expect.stringContaining('"type":"draw_card"')
    );

    // Simulate updated game state after drawing card
    const updatedGameState = {
      ...mockGameState,
      playerStates: {
        ...mockGameState.playerStates,
        'player-1': {
          ...mockGameState.playerStates['player-1'],
          hand: [
            ...mockGameState.playerStates['player-1'].hand,
            { id: 'card-4', suit: 'clubs', value: '3', color: 'black' },
          ],
        },
      },
    };

    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: updatedGameState,
        }),
      }));
    }

    // Check that the player's hand is updated
    await waitFor(() => {
      expect(screen.getAllByTestId('card')).toHaveLength(3);
    });
  });

  test('shows winner when game is over', async () => {
    render(<GamePage />);

    // Mock WebSocket connection
    const mockWs = new MockWebSocket();
    if (mockWs.onopen) {
      mockWs.onopen(new Event('open'));
    }

    // Send initial game state
    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: mockGameState,
        }),
      }));
    }

    // Wait for game board to appear
    await waitFor(() => {
      expect(screen.getByTestId('game-board')).toBeInTheDocument();
    });

    // Send updated game state with game over
    const gameOverState = {
      ...mockGameState,
      gameOver: true,
      winnerId: 'player-1',
      status: 'completed',
    };

    if (mockWs.onmessage) {
      mockWs.onmessage(new MessageEvent('message', {
        data: JSON.stringify({
          type: 'game_state',
          data: gameOverState,
        }),
      }));
    }

    // Check winner display
    await waitFor(() => {
      expect(screen.getByTestId('winner-display')).toBeInTheDocument();
      expect(screen.getByTestId('winner-display')).toHaveTextContent('Game Over!');
      expect(screen.getByTestId('winner-display')).toHaveTextContent('Winner: Test Player');
    });
  });
});
