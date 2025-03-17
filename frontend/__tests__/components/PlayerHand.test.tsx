import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import PlayerHand from '../../src/components/PlayerHand';
import { Card, PlayerHandProps } from '../../src/types/game';

describe('PlayerHand Component', () => {
  const mockCards: Card[] = [
    { suit: 'hearts', value: '8', playable: true },
    { suit: 'diamonds', value: 'K', playable: false },
    { suit: 'spades', value: 'A', playable: true },
  ];

  const mockProps: PlayerHandProps = {
    cards: mockCards,
    onPlayCard: jest.fn(),
    isCurrentPlayer: true,
    currentSuit: 'hearts',
    currentValue: '8',
    sortOrder: 'suit',
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all cards in hand', () => {
    render(<PlayerHand {...mockProps} />);

    expect(screen.getByText('8♥')).toBeInTheDocument();
    expect(screen.getByText('K♦')).toBeInTheDocument();
    expect(screen.getByText('A♠')).toBeInTheDocument();
  });

  it('handles card play when card is playable', () => {
    render(<PlayerHand {...mockProps} />);

    fireEvent.click(screen.getByText('8♥'));

    expect(mockProps.onPlayCard).toHaveBeenCalledWith(mockCards[0]);
  });

  it('does not allow playing unplayable cards', () => {
    render(<PlayerHand {...mockProps} />);

    fireEvent.click(screen.getByText('K♦'));

    expect(mockProps.onPlayCard).not.toHaveBeenCalled();
  });

  it('disables all cards when not current player', () => {
    render(<PlayerHand {...mockProps} isCurrentPlayer={false} />);

    const cards = screen.getAllByRole('button');
    cards.forEach(card => {
      expect(card).toBeDisabled();
    });
  });

  it('sorts cards by suit when sortOrder is suit', () => {
    const unsortedCards: Card[] = [
      { suit: 'spades', value: 'A', playable: true },
      { suit: 'hearts', value: '8', playable: true },
      { suit: 'diamonds', value: 'K', playable: false },
    ];

    render(
      <PlayerHand
        {...mockProps}
        cards={unsortedCards}
        sortOrder="suit"
      />
    );

    const cardElements = screen.getAllByRole('button');
    expect(cardElements[0]).toHaveTextContent('8♥');
    expect(cardElements[1]).toHaveTextContent('K♦');
    expect(cardElements[2]).toHaveTextContent('A♠');
  });

  it('sorts cards by value when sortOrder is value', () => {
    const unsortedCards: Card[] = [
      { suit: 'spades', value: 'A', playable: true },
      { suit: 'hearts', value: '8', playable: true },
      { suit: 'diamonds', value: 'K', playable: false },
    ];

    render(
      <PlayerHand
        {...mockProps}
        cards={unsortedCards}
        sortOrder="value"
      />
    );

    const cardElements = screen.getAllByRole('button');
    expect(cardElements[0]).toHaveTextContent('8♥');
    expect(cardElements[1]).toHaveTextContent('K♦');
    expect(cardElements[2]).toHaveTextContent('A♠');
  });

  it('applies playable styles to playable cards', () => {
    render(<PlayerHand {...mockProps} />);

    const playableCard = screen.getByText('8♥').parentElement;
    const unplayableCard = screen.getByText('K♦').parentElement;

    expect(playableCard).toHaveClass('playable');
    expect(unplayableCard).not.toHaveClass('playable');
  });

  it('shows empty hand message when no cards', () => {
    render(<PlayerHand {...mockProps} cards={[]} />);

    expect(screen.getByText('No cards in hand')).toBeInTheDocument();
  });

  it('highlights cards matching current suit or value', () => {
    render(<PlayerHand {...mockProps} />);

    const matchingSuitCard = screen.getByText('8♥').parentElement;
    const matchingValueCard = screen.getByText('8♥').parentElement;
    const nonMatchingCard = screen.getByText('K♦').parentElement;

    expect(matchingSuitCard).toHaveClass('matching');
    expect(matchingValueCard).toHaveClass('matching');
    expect(nonMatchingCard).not.toHaveClass('matching');
  });
});
