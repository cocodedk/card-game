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

    // Find cards by their value and suit data-testid elements
    const cardValues = screen.getAllByTestId('card-value');
    const cardSuits = screen.getAllByTestId('card-suit');

    // Check that we have the right values
    expect(cardValues.some(el => el.textContent === '8')).toBeTruthy();
    expect(cardValues.some(el => el.textContent === 'K')).toBeTruthy();
    expect(cardValues.some(el => el.textContent === 'A')).toBeTruthy();

    // Check that we have the right suits
    expect(cardSuits.some(el => el.textContent === '♥')).toBeTruthy();
    expect(cardSuits.some(el => el.textContent === '♦')).toBeTruthy();
    expect(cardSuits.some(el => el.textContent === '♠')).toBeTruthy();
  });

  // Use a helper method to find a card by its value and suit
  const findCardByValueAndSuit = (value: string, suit: string) => {
    const cards = screen.getAllByTestId('card');
    return cards.find(card => {
      const cardValue = card.querySelector(`[data-testid="card-value"]`);
      const cardSuit = card.querySelector(`[data-testid="card-suit"]`);
      return cardValue?.textContent === value && cardSuit?.textContent === suit;
    });
  };

  it('handles card play when card is playable', () => {
    render(<PlayerHand {...mockProps} />);

    const card = findCardByValueAndSuit('8', '♥');
    fireEvent.click(card!);

    expect(mockProps.onPlayCard).toHaveBeenCalledWith(mockCards[0]);
  });

  it('does not allow playing unplayable cards', () => {
    render(<PlayerHand {...mockProps} />);

    const card = findCardByValueAndSuit('K', '♦');
    fireEvent.click(card!);

    expect(mockProps.onPlayCard).not.toHaveBeenCalled();
  });

  it('disables all cards when not current player', () => {
    render(<PlayerHand {...mockProps} isCurrentPlayer={false} />);

    const cards = screen.getAllByTestId('card');
    cards.forEach(card => {
      expect(card).toHaveAttribute('aria-disabled', 'true');
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

    const containers = screen.getAllByTestId('card-container');

    // First container should have hearts
    const heartsContainer = containers.find(container =>
      container.querySelector('[data-testid="card-suit"]')?.textContent === '♥'
    );

    // Second container should have diamonds
    const diamondsContainer = containers.find(container =>
      container.querySelector('[data-testid="card-suit"]')?.textContent === '♦'
    );

    // Third container should have spades
    const spadesContainer = containers.find(container =>
      container.querySelector('[data-testid="card-suit"]')?.textContent === '♠'
    );

    expect(heartsContainer).toBeDefined();
    expect(diamondsContainer).toBeDefined();
    expect(spadesContainer).toBeDefined();
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

    const playableCard = findCardByValueAndSuit('8', '♥');
    const unplayableCard = findCardByValueAndSuit('K', '♦');

    expect(playableCard).toHaveClass('cursor-pointer');
    expect(playableCard).not.toHaveClass('cursor-not-allowed');
    expect(unplayableCard).toHaveClass('cursor-not-allowed');
    expect(unplayableCard).not.toHaveClass('cursor-pointer');
  });

  it('shows empty hand message when no cards', () => {
    render(<PlayerHand {...mockProps} cards={[]} />);

    expect(screen.queryByTestId('card')).not.toBeInTheDocument();
  });

  it('highlights cards matching current suit or value', () => {
    render(<PlayerHand {...mockProps} />);

    const matchingCard = findCardByValueAndSuit('8', '♥');
    const nonMatchingCard = findCardByValueAndSuit('K', '♦');

    expect(matchingCard).toHaveClass('border-blue-500');
    expect(nonMatchingCard).not.toHaveClass('border-blue-500');
  });
});
