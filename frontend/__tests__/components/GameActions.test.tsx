import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import GameActions from '../../src/components/GameActions';
import { GameActionsProps } from '../../src/types/game';

describe('GameActions Component', () => {
  const mockProps: GameActionsProps = {
    isCurrentPlayer: true,
    onDrawCard: jest.fn(),
    onPassTurn: jest.fn(),
    onAnnounceOneCard: jest.fn(),
    canPass: true,
    canDraw: true,
    cardsInHand: 2,
    hasAnnouncedOneCard: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all action buttons when current player', () => {
    render(<GameActions {...mockProps} />);

    expect(screen.getByRole('button', { name: 'Draw Card' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Pass Turn' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Announce One Card' })).toBeInTheDocument();
  });

  it('disables buttons when not current player', () => {
    render(<GameActions {...mockProps} isCurrentPlayer={false} />);

    expect(screen.getByRole('button', { name: 'Draw Card' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Pass Turn' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Announce One Card' })).toBeDisabled();
  });

  it('disables draw button when canDraw is false', () => {
    render(<GameActions {...mockProps} canDraw={false} />);

    expect(screen.getByRole('button', { name: 'Draw Card' })).toBeDisabled();
  });

  it('disables pass button when canPass is false', () => {
    render(<GameActions {...mockProps} canPass={false} />);

    expect(screen.getByRole('button', { name: 'Pass Turn' })).toBeDisabled();
  });

  it('handles draw card action', () => {
    render(<GameActions {...mockProps} />);

    fireEvent.click(screen.getByRole('button', { name: 'Draw Card' }));

    expect(mockProps.onDrawCard).toHaveBeenCalled();
  });

  it('handles pass turn action', () => {
    render(<GameActions {...mockProps} />);

    fireEvent.click(screen.getByRole('button', { name: 'Pass Turn' }));

    expect(mockProps.onPassTurn).toHaveBeenCalled();
  });

  it('handles announce one card action', () => {
    render(<GameActions {...mockProps} cardsInHand={1} />);

    fireEvent.click(screen.getByRole('button', { name: 'Announce One Card' }));

    expect(mockProps.onAnnounceOneCard).toHaveBeenCalled();
  });

  it('disables announce one card button when already announced', () => {
    render(<GameActions {...mockProps} hasAnnouncedOneCard={true} />);

    expect(screen.getByRole('button', { name: 'Announce One Card' })).toBeDisabled();
  });

  it('disables announce one card button when more than one card in hand', () => {
    render(<GameActions {...mockProps} cardsInHand={3} />);

    expect(screen.getByRole('button', { name: 'Announce One Card' })).toBeDisabled();
  });

  it('enables announce one card button when exactly one card in hand', () => {
    render(<GameActions {...mockProps} cardsInHand={1} />);

    expect(screen.getByRole('button', { name: 'Announce One Card' })).toBeEnabled();
  });
});
