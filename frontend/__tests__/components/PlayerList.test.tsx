import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import PlayerList from '../../src/components/PlayerList';

describe('PlayerList Component', () => {
  const mockPlayers = [
    {
      id: 'player1',
      name: 'Player 1',
      status: 'online' as const,
      ready: true,
      avatar_url: 'https://example.com/avatar1.jpg',
    },
    {
      id: 'player2',
      name: 'Player 2',
      status: 'offline' as const,
      ready: false,
    },
    {
      id: 'player3',
      name: 'Player 3',
      status: 'in_game' as const,
      ready: false,
    },
  ];

  const mockOnRemovePlayer = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all players', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        showRemoveButton={false}
      />
    );

    const playerItems = screen.getAllByRole('listitem');
    expect(playerItems).toHaveLength(3);

    // Check that each player's name appears in the list
    const player1NameEl = screen.getByText((content, element) => {
      return element?.textContent === 'Player 1 (You)';
    });
    const player2NameEl = screen.getByText('Player 2');
    const player3NameEl = screen.getByText('Player 3');

    expect(player1NameEl).toBeInTheDocument();
    expect(player2NameEl).toBeInTheDocument();
    expect(player3NameEl).toBeInTheDocument();
  });

  it('shows (You) next to current player', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        showRemoveButton={false}
      />
    );

    const playerItems = screen.getAllByRole('listitem');
    const currentPlayerItem = playerItems[0];

    expect(within(currentPlayerItem).getByText((content, element) => {
      return element?.textContent === 'Player 1 (You)';
    })).toBeInTheDocument();
  });

  it('displays player status correctly', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        showRemoveButton={false}
      />
    );

    const onlineStatus = screen.getByText('online');
    const offlineStatus = screen.getByText('offline');
    const inGameStatus = screen.getByText('in_game');

    expect(onlineStatus).toBeInTheDocument();
    expect(onlineStatus).toHaveClass('status-online');
    expect(offlineStatus).toBeInTheDocument();
    expect(offlineStatus).toHaveClass('status-offline');
    expect(inGameStatus).toBeInTheDocument();
    expect(inGameStatus).toHaveClass('status-in_game');
  });

  it('shows ready indicator for ready players', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        showRemoveButton={false}
      />
    );

    const readyIndicators = screen.getAllByRole('status');
    expect(readyIndicators).toHaveLength(1);
    expect(readyIndicators[0]).toHaveTextContent('Ready');
  });

  it('shows remove button when enabled', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        onRemovePlayer={mockOnRemovePlayer}
        showRemoveButton={true}
      />
    );

    // Should show remove buttons for all players except current player
    const removeButtons = screen.getAllByRole('button');
    expect(removeButtons).toHaveLength(2);
  });

  it('calls onRemovePlayer when remove button is clicked', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        onRemovePlayer={mockOnRemovePlayer}
        showRemoveButton={true}
      />
    );

    const removeButton = screen.getByLabelText('Remove Player 2');
    fireEvent.click(removeButton);

    expect(mockOnRemovePlayer).toHaveBeenCalledWith('player2');
  });

  it('renders player avatar when available', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        showRemoveButton={false}
      />
    );

    const avatar = screen.getByAltText("Player 1's avatar");
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', 'https://example.com/avatar1.jpg');
  });

  it('does not show remove button for current player', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        onRemovePlayer={mockOnRemovePlayer}
        showRemoveButton={true}
      />
    );

    expect(screen.queryByLabelText('Remove Player 1')).not.toBeInTheDocument();
  });

  it('applies ready class to ready players', () => {
    render(
      <PlayerList
        players={mockPlayers}
        currentPlayerId="player1"
        showRemoveButton={false}
      />
    );

    const playerItems = screen.getAllByRole('listitem');
    expect(playerItems[0]).toHaveClass('player-ready');
    expect(playerItems[1]).not.toHaveClass('player-ready');
  });
});
