import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SpecialCardActions from '../../src/components/SpecialCardActions';
import { Card, SpecialCardActionsProps, Player } from '../../src/types/game';

describe('SpecialCardActions Component', () => {
  const mockCard: Card = {
    suit: 'hearts',
    value: '8',
    playable: true,
  };

  const mockPlayers: { id: string; name: string; }[] = [
    { id: 'player1', name: 'Player 1' },
    { id: 'player2', name: 'Player 2' },
  ];

  const mockProps: SpecialCardActionsProps = {
    isOpen: true,
    onClose: jest.fn(),
    actionType: 'suit-selection',
    onSuitSelect: jest.fn(),
    onTargetSelect: jest.fn(),
    onCounterAction: jest.fn(),
    availablePlayers: mockPlayers,
    cardInPlay: mockCard,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders suit selection modal', () => {
    render(<SpecialCardActions {...mockProps} />);

    expect(screen.getByText('Select a Suit')).toBeInTheDocument();
    expect(screen.getByTestId('suit-hearts')).toBeInTheDocument();
    expect(screen.getByTestId('suit-diamonds')).toBeInTheDocument();
    expect(screen.getByTestId('suit-clubs')).toBeInTheDocument();
    expect(screen.getByTestId('suit-spades')).toBeInTheDocument();
  });

  it('handles suit selection', () => {
    render(<SpecialCardActions {...mockProps} />);

    fireEvent.click(screen.getByTestId('suit-hearts'));

    expect(mockProps.onSuitSelect).toHaveBeenCalledWith('hearts');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('renders target selection modal', () => {
    render(<SpecialCardActions {...mockProps} actionType="target-player" />);

    expect(screen.getByText('Select a Target Player')).toBeInTheDocument();
    expect(screen.getByTestId('player-player1')).toBeInTheDocument();
    expect(screen.getByTestId('player-player2')).toBeInTheDocument();
  });

  it('handles target selection', () => {
    render(<SpecialCardActions {...mockProps} actionType="target-player" />);

    fireEvent.click(screen.getByTestId('player-player1'));

    expect(mockProps.onTargetSelect).toHaveBeenCalledWith('player1');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('renders counter action modal', () => {
    render(<SpecialCardActions {...mockProps} actionType="counter-action" />);

    expect(screen.getByText('Counter Action Required')).toBeInTheDocument();
    expect(screen.getByTestId('counter-action-button')).toBeInTheDocument();
    expect(screen.getByTestId('accept-action')).toBeInTheDocument();
  });

  it('handles counter action', () => {
    render(<SpecialCardActions {...mockProps} actionType="counter-action" />);

    fireEvent.click(screen.getByTestId('counter-action-button'));

    expect(mockProps.onCounterAction).toHaveBeenCalledWith('counter');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('handles pass action', () => {
    render(<SpecialCardActions {...mockProps} actionType="counter-action" />);

    fireEvent.click(screen.getByTestId('accept-action'));

    expect(mockProps.onCounterAction).toHaveBeenCalledWith('accept');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('does not render when isOpen is false', () => {
    render(<SpecialCardActions {...mockProps} isOpen={false} />);

    expect(screen.queryByText('Select a Suit')).not.toBeInTheDocument();
    expect(screen.queryByText('Select a Target')).not.toBeInTheDocument();
    expect(screen.queryByText('Counter Action')).not.toBeInTheDocument();
  });
});
