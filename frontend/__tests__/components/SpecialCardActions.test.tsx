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
    expect(screen.getByRole('button', { name: 'Hearts' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Diamonds' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Clubs' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Spades' })).toBeInTheDocument();
  });

  it('handles suit selection', () => {
    render(<SpecialCardActions {...mockProps} />);

    fireEvent.click(screen.getByRole('button', { name: 'Hearts' }));

    expect(mockProps.onSuitSelect).toHaveBeenCalledWith('hearts');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('renders target selection modal', () => {
    render(<SpecialCardActions {...mockProps} actionType="target-player" />);

    expect(screen.getByText('Select a Target')).toBeInTheDocument();
    expect(screen.getByText('Player 1')).toBeInTheDocument();
    expect(screen.getByText('Player 2')).toBeInTheDocument();
  });

  it('handles target selection', () => {
    render(<SpecialCardActions {...mockProps} actionType="target-player" />);

    fireEvent.click(screen.getByText('Player 1'));

    expect(mockProps.onTargetSelect).toHaveBeenCalledWith('player1');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('renders counter action modal', () => {
    render(<SpecialCardActions {...mockProps} actionType="counter-action" />);

    expect(screen.getByText('Counter Action')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Counter' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pass' })).toBeInTheDocument();
  });

  it('handles counter action', () => {
    render(<SpecialCardActions {...mockProps} actionType="counter-action" />);

    fireEvent.click(screen.getByRole('button', { name: 'Counter' }));

    expect(mockProps.onCounterAction).toHaveBeenCalledWith('counter');
    expect(mockProps.onClose).toHaveBeenCalled();
  });

  it('handles pass action', () => {
    render(<SpecialCardActions {...mockProps} actionType="counter-action" />);

    fireEvent.click(screen.getByRole('button', { name: 'Pass' }));

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
