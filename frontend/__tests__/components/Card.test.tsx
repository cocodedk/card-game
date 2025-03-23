import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import Card from '../../src/components/Card';
import { CardProps } from '../../src/types/game';

describe('Card Component', () => {
  const mockCard = {
    suit: 'hearts',
    value: '8',
    playable: true,
  };

  const mockProps: CardProps = {
    card: mockCard,
    onPlay: jest.fn(),
    isPlayable: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders card with correct suit and value', () => {
    render(<Card {...mockProps} />);

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue.textContent).toBe('8');
    expect(cardSuit.textContent).toBe('♥');
  });

  it('handles card play when playable', () => {
    render(<Card {...mockProps} />);

    fireEvent.click(screen.getByTestId('card'));

    expect(mockProps.onPlay).toHaveBeenCalledWith(mockCard);
  });

  it('disables card when not playable', () => {
    render(<Card {...mockProps} isPlayable={false} />);

    expect(screen.getByTestId('card')).toHaveAttribute('aria-disabled', 'true');
  });

  it('applies correct color for hearts suit', () => {
    render(<Card {...mockProps} />);

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue).toHaveClass('text-red-600');
    expect(cardSuit).toHaveClass('text-red-600');
  });

  it('applies correct color for diamonds suit', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'diamonds' }}
      />
    );

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue).toHaveClass('text-red-600');
    expect(cardSuit).toHaveClass('text-red-600');
  });

  it('applies correct color for spades suit', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'spades' }}
      />
    );

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue).toHaveClass('text-gray-900');
    expect(cardSuit).toHaveClass('text-gray-900');
  });

  it('applies correct color for clubs suit', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'clubs' }}
      />
    );

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue).toHaveClass('text-gray-900');
    expect(cardSuit).toHaveClass('text-gray-900');
  });

  it('displays correct suit symbol for hearts', () => {
    render(<Card {...mockProps} />);

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue.textContent).toBe('8');
    expect(cardSuit.textContent).toBe('♥');
  });

  it('displays correct suit symbol for diamonds', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'diamonds' }}
      />
    );

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue.textContent).toBe('8');
    expect(cardSuit.textContent).toBe('♦');
  });

  it('displays correct suit symbol for spades', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'spades' }}
      />
    );

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue.textContent).toBe('8');
    expect(cardSuit.textContent).toBe('♠');
  });

  it('displays correct suit symbol for clubs', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'clubs' }}
      />
    );

    const cardValue = screen.getByTestId('card-value');
    const cardSuit = screen.getByTestId('card-suit');

    expect(cardValue.textContent).toBe('8');
    expect(cardSuit.textContent).toBe('♣');
  });

  it('applies playable styles when card is playable', () => {
    render(<Card {...mockProps} />);

    expect(screen.getByTestId('card')).toHaveClass('cursor-pointer');
    expect(screen.getByTestId('card')).toHaveClass('border-blue-500');
  });

  it('does not apply playable styles when card is not playable', () => {
    render(<Card {...mockProps} isPlayable={false} />);

    expect(screen.getByTestId('card')).toHaveClass('cursor-not-allowed');
    expect(screen.getByTestId('card')).toHaveClass('border-gray-300');
  });

  it('applies hover effect styles when playable', () => {
    render(<Card {...mockProps} />);

    expect(screen.getByTestId('card')).toHaveClass('hover:scale-105');
  });

  it('does not apply hover effect styles when not playable', () => {
    render(<Card {...mockProps} isPlayable={false} />);

    expect(screen.getByTestId('card')).not.toHaveClass('hover:scale-105');
  });
});
