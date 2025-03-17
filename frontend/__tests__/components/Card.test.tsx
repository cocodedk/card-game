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

    expect(screen.getByText('8♥')).toBeInTheDocument();
  });

  it('handles card play when playable', () => {
    render(<Card {...mockProps} />);

    fireEvent.click(screen.getByRole('button'));

    expect(mockProps.onPlay).toHaveBeenCalledWith(mockCard);
  });

  it('disables card when not playable', () => {
    render(<Card {...mockProps} isPlayable={false} />);

    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('applies correct color for hearts suit', () => {
    render(<Card {...mockProps} />);

    expect(screen.getByRole('button')).toHaveClass('text-red-600');
  });

  it('applies correct color for diamonds suit', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'diamonds' }}
      />
    );

    expect(screen.getByRole('button')).toHaveClass('text-red-600');
  });

  it('applies correct color for spades suit', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'spades' }}
      />
    );

    expect(screen.getByRole('button')).toHaveClass('text-gray-900');
  });

  it('applies correct color for clubs suit', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'clubs' }}
      />
    );

    expect(screen.getByRole('button')).toHaveClass('text-gray-900');
  });

  it('displays correct suit symbol for hearts', () => {
    render(<Card {...mockProps} />);

    expect(screen.getByText('8♥')).toBeInTheDocument();
  });

  it('displays correct suit symbol for diamonds', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'diamonds' }}
      />
    );

    expect(screen.getByText('8♦')).toBeInTheDocument();
  });

  it('displays correct suit symbol for spades', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'spades' }}
      />
    );

    expect(screen.getByText('8♠')).toBeInTheDocument();
  });

  it('displays correct suit symbol for clubs', () => {
    render(
      <Card
        {...mockProps}
        card={{ ...mockCard, suit: 'clubs' }}
      />
    );

    expect(screen.getByText('8♣')).toBeInTheDocument();
  });

  it('applies playable styles when card is playable', () => {
    render(<Card {...mockProps} />);

    expect(screen.getByRole('button')).toHaveClass('playable');
  });

  it('does not apply playable styles when card is not playable', () => {
    render(<Card {...mockProps} isPlayable={false} />);

    expect(screen.getByRole('button')).not.toHaveClass('playable');
  });

  it('applies hover effect styles when playable', () => {
    render(<Card {...mockProps} />);

    expect(screen.getByRole('button')).toHaveClass('hover:scale-110');
  });

  it('does not apply hover effect styles when not playable', () => {
    render(<Card {...mockProps} isPlayable={false} />);

    expect(screen.getByRole('button')).not.toHaveClass('hover:scale-110');
  });
});
