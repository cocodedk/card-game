import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PlayerManagement from '../../src/components/PlayerManagement';
import { Player } from '../../src/types/game';

jest.mock('../../src/components/PlayerSearch', () => {
  return function MockPlayerSearch({ onSelectPlayer }: { onSelectPlayer: (player: any) => void }) {
    return (
      <div data-testid="player-search">
        <button onClick={() => onSelectPlayer({ id: 'new-player', name: 'New Player' })}>
          Select Player
        </button>
      </div>
    );
  };
});

describe('PlayerManagement Component', () => {
  const mockPlayers: Player[] = [
    { id: 'player1', name: 'Player 1', status: 'online', ready: true },
    { id: 'player2', name: 'Player 2', status: 'online', ready: false },
  ];

  const mockProps = {
    gameId: 'game123',
    currentPlayerId: 'player1',
    players: mockPlayers,
    onInvitePlayer: jest.fn(),
    onRemovePlayer: jest.fn(),
    onToggleReady: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all sections', () => {
    render(<PlayerManagement {...mockProps} />);

    expect(screen.getByText('Invite Players')).toBeInTheDocument();
    expect(screen.getByTestId('player-search')).toBeInTheDocument();
    expect(screen.getByText('Players')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Not Ready' })).toBeInTheDocument();
  });

  it('handles player invitation', () => {
    render(<PlayerManagement {...mockProps} />);

    fireEvent.click(screen.getByText('Select Player'));

    expect(mockProps.onInvitePlayer).toHaveBeenCalledWith('new-player');
  });

  it('handles player removal', () => {
    render(<PlayerManagement {...mockProps} />);

    fireEvent.click(screen.getByLabelText('Remove Player 2'));

    expect(mockProps.onRemovePlayer).toHaveBeenCalledWith('player2');
  });

  it('handles ready toggle', () => {
    render(<PlayerManagement {...mockProps} />);

    fireEvent.click(screen.getByRole('button', { name: 'Not Ready' }));

    expect(mockProps.onToggleReady).toHaveBeenCalled();
  });

  it('shows correct ready button state', () => {
    const notReadyPlayers: Player[] = [
      { id: 'player1', name: 'Player 1', status: 'online', ready: false },
      { id: 'player2', name: 'Player 2', status: 'online', ready: false },
    ];

    const propsWithNotReady = {
      ...mockProps,
      players: notReadyPlayers,
    };

    const { rerender } = render(<PlayerManagement {...propsWithNotReady} />);
    expect(screen.getByRole('button', { name: 'Ready' })).toBeInTheDocument();

    rerender(<PlayerManagement {...mockProps} />);
    expect(screen.getByRole('button', { name: 'Not Ready' })).toBeInTheDocument();
  });

  it('displays correct number of players', () => {
    render(<PlayerManagement {...mockProps} />);

    expect(screen.getByText('Player 1')).toBeInTheDocument();
    expect(screen.getByText('Player 2')).toBeInTheDocument();
  });

  it('shows current player indicator', () => {
    render(<PlayerManagement {...mockProps} />);

    expect(screen.getByText('Player 1 (You)')).toBeInTheDocument();
  });

  it('applies ready styling to ready button', () => {
    render(<PlayerManagement {...mockProps} />);

    const readyButton = screen.getByRole('button', { name: 'Not Ready' });
    expect(readyButton).toHaveClass('ready');
  });
});
