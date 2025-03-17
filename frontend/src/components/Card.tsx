import React from 'react';
import { Card as CardType, CardProps } from '../types/game';

const Card: React.FC<CardProps> = ({ card, onPlay, isPlayable }) => {
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (isPlayable) {
      onPlay(card);
    }
  };

  const getSuitColor = (suit: string) => {
    return ['hearts', 'diamonds'].includes(suit.toLowerCase()) ? 'text-red-600' : 'text-gray-900';
  };

  const getSuitSymbol = (suit: string) => {
    const symbols: { [key: string]: string } = {
      hearts: '♥',
      diamonds: '♦',
      clubs: '♣',
      spades: '♠',
    };
    return symbols[suit.toLowerCase()] || suit;
  };

  return (
    <div
      className={`
        relative w-24 h-36 rounded-lg border-2 bg-white shadow-md
        transform transition-transform duration-200
        ${isPlayable ? 'cursor-pointer hover:scale-105' : 'cursor-not-allowed opacity-70'}
        ${isPlayable ? 'border-blue-500' : 'border-gray-300'}
      `}
      onClick={handleClick}
      data-testid="card"
      role="button"
      aria-disabled={!isPlayable}
    >
      <div className="absolute top-2 left-2">
        <span className={`text-lg font-bold ${getSuitColor(card.suit)}`}>
          {card.value}
        </span>
      </div>
      <div className="absolute top-8 left-1/2 transform -translate-x-1/2">
        <span className={`text-4xl ${getSuitColor(card.suit)}`}>
          {getSuitSymbol(card.suit)}
        </span>
      </div>
      <div className="absolute bottom-2 right-2 rotate-180">
        <span className={`text-lg font-bold ${getSuitColor(card.suit)}`}>
          {card.value}
        </span>
      </div>
    </div>
  );
};

export default Card;
