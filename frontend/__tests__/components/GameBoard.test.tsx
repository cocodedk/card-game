import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import GameBoard from '@/components/GameBoard';
import { Card, Player, GameState } from '@/types/game';

describe('GameBoard Component', () => {
  const mockPlayers: Player[] = [
    { id: 'player1', name: 'Player 1', status: 'online', ready: true },
    { id: 'player2', name: 'Player 2', status: 'online', ready: true },
    { id: 'player3', name: 'Player 3', status: 'online', ready: true },
  ];

  const mockHand: Card[] = [
    { suit: 'hearts', value: '8', playable: true },
    { suit: 'diamonds', value: 'K', playable: false },
    { suit: 'spades', value: 'A', playable: true },
  ];

  const mockGameState: GameState = {
    currentPlayer: 'player1',
    nextPlayer: 'player2',
    direction: 'clockwise',
    playerStates: {
      player1: {
        hand: mockHand,
        announcedOneCard: false,
        penalties: 0,
      },
      player2: {
        hand: [],
        announcedOneCard: false,
        penalties: 0,
      },
      player3: {
        hand: [],
        announcedOneCard: false,
        penalties: 0,
      },
    },
    discardPile: [{ suit: 'hearts', value: '7' }],
    currentSuit: 'hearts',
    gameOver: false,
  };

  const mockProps = {
    gameId: 'game123',
    players: mockPlayers,
    currentPlayerId: 'player1',
    gameState: mockGameState,
    onPlayCard: jest.fn(),
    onDrawCard: jest.fn(),
    onPassTurn: jest.fn(),
    onAnnounceOneCard: jest.fn(),
    onSuitSelect: jest.fn(),
    onTargetSelect: jest.fn(),
    onCounterAction: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders game board with all components', () => {
    render(<GameBoard {...mockProps} />);

    const playerElements = screen.getAllByText(/Player [1-3]/);
    expect(playerElements).toHaveLength(5); // 3 player names + current turn + next turn

    const discardValue = screen.getByTestId('discard-value');
    const discardSuit = screen.getByTestId('discard-suit');
    expect(discardValue).toHaveTextContent('7');
    expect(discardSuit).toHaveTextContent('♥');
  });

  it('shows current player indicator', () => {
    render(<GameBoard {...mockProps} />);

    expect(screen.getByText('Current Turn: Player 1')).toBeInTheDocument();
  });

  it('shows next player indicator', () => {
    render(<GameBoard {...mockProps} />);

    expect(screen.getByText('Next Turn: Player 2')).toBeInTheDocument();
  });

  it('shows game direction', () => {
    render(<GameBoard {...mockProps} />);

    expect(screen.getByText('Direction: Clockwise')).toBeInTheDocument();
  });

  it('shows current suit', () => {
    render(<GameBoard {...mockProps} />);

    expect(screen.getByText('Current Suit: Hearts')).toBeInTheDocument();
  });

  it('handles card play', () => {
    render(<GameBoard {...mockProps} />);

    const cards = screen.getAllByTestId('card');
    const playableCard = cards[0]; // First card is playable in our mock data
    fireEvent.click(playableCard);

    expect(mockProps.onPlayCard).toHaveBeenCalledWith(mockHand[0]);
  });

  it('handles draw card', () => {
    render(<GameBoard {...mockProps} />);

    fireEvent.click(screen.getByTestId('draw-card-button'));

    expect(mockProps.onDrawCard).toHaveBeenCalled();
  });

  it('handles pass turn', () => {
    render(<GameBoard {...mockProps} />);

    fireEvent.click(screen.getByTestId('pass-turn-button'));

    expect(mockProps.onPassTurn).toHaveBeenCalled();
  });

  it('handles announce one card', () => {
    const gameStateWithOneCard = {
      ...mockGameState,
      playerStates: {
        ...mockGameState.playerStates,
        player1: {
          ...mockGameState.playerStates.player1,
          hand: [mockHand[0]],
        },
      },
    };

    render(<GameBoard {...mockProps} gameState={gameStateWithOneCard} />);

    fireEvent.click(screen.getByTestId('announce-one-card-button'));

    expect(mockProps.onAnnounceOneCard).toHaveBeenCalled();
  });

  it('shows game over state', () => {
    const gameOverState = {
      ...mockGameState,
      gameOver: true,
      winnerId: 'player1',
    };

    render(<GameBoard {...mockProps} gameState={gameOverState} />);

    expect(screen.getByText('Game Over!')).toBeInTheDocument();
    expect(screen.getByText('Winner: Player 1')).toBeInTheDocument();
  });

  it('shows penalties', () => {
    const stateWithPenalties = {
      ...mockGameState,
      playerStates: {
        ...mockGameState.playerStates,
        player1: {
          ...mockGameState.playerStates.player1,
          penalties: 2,
        },
      },
    };

    render(<GameBoard {...mockProps} gameState={stateWithPenalties} />);

    expect(screen.getByText('Penalties: 2')).toBeInTheDocument();
  });

  it('shows announced one card status', () => {
    const stateWithAnnouncement = {
      ...mockGameState,
      playerStates: {
        ...mockGameState.playerStates,
        player2: {
          ...mockGameState.playerStates.player2,
          announcedOneCard: true,
        },
      },
    };

    render(<GameBoard {...mockProps} gameState={stateWithAnnouncement} />);

    expect(screen.getByText('Has one card!')).toBeInTheDocument();
  });

  it('disables actions when not current player', () => {
    render(<GameBoard {...mockProps} currentPlayerId="player2" />);

    expect(screen.getByTestId('draw-card-button')).toBeDisabled();
    expect(screen.getByTestId('pass-turn-button')).toBeDisabled();
  });
});
