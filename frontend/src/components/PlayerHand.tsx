import React, { useMemo, useState } from 'react';
import { Card as CardType, PlayerHandProps, SortedHand } from '../types/game';
import Card from './Card';

const PlayerHand: React.FC<PlayerHandProps> = ({
  cards,
  onPlayCard,
  isCurrentPlayer,
  currentSuit,
  currentValue,
  sortOrder = 'suit',
}) => {
  const [isDragging, setIsDragging] = useState(false);

  const isPlayable = (card: CardType): boolean => {
    if (!isCurrentPlayer) return false;
    if (!currentSuit && !currentValue) return true;
    return card.suit === currentSuit || card.value === currentValue;
  };

  const sortedCards = useMemo(() => {
    if (sortOrder === 'suit') {
      const sorted: SortedHand = {};
      cards.forEach((card) => {
        if (!sorted[card.suit]) {
          sorted[card.suit] = [];
        }
        sorted[card.suit].push(card);
      });
      // Sort each suit by value
      Object.keys(sorted).forEach((suit) => {
        sorted[suit].sort((a, b) => {
          const values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
          return values.indexOf(a.value) - values.indexOf(b.value);
        });
      });
      return sorted;
    } else {
      // Sort by value
      return {
        all: [...cards].sort((a, b) => {
          const values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
          return values.indexOf(a.value) - values.indexOf(b.value);
        }),
      };
    }
  }, [cards, sortOrder]);

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, card: CardType) => {
    if (!isPlayable(card)) {
      e.preventDefault();
      return;
    }
    setIsDragging(true);
    e.dataTransfer.setData('text/plain', JSON.stringify(card));
  };

  const handleDragEnd = () => {
    setIsDragging(false);
  };

  const renderCards = (cardsToRender: CardType[]) => {
    return cardsToRender.map((card, index) => (
      <div
        key={`${card.suit}-${card.value}`}
        className={`
          transform transition-transform duration-200
          ${index > 0 ? '-ml-16' : ''}
          ${isDragging ? 'hover:translate-y-[-1rem]' : ''}
        `}
        draggable={isPlayable(card)}
        onDragStart={(e) => handleDragStart(e, card)}
        onDragEnd={handleDragEnd}
      >
        <Card
          card={card}
          onPlay={onPlayCard}
          isPlayable={isPlayable(card)}
        />
      </div>
    ));
  };

  return (
    <div
      className="flex flex-col gap-4 p-4"
      data-testid="player-hand"
    >
      {sortOrder === 'suit' ? (
        Object.entries(sortedCards).map(([suit, suitCards]) => (
          <div key={suit} className="flex flex-row flex-wrap" data-testid="card-container">
            {renderCards(suitCards)}
          </div>
        ))
      ) : (
        <div className="flex flex-row flex-wrap" data-testid="card-container">
          {renderCards(sortedCards.all)}
        </div>
      )}
    </div>
  );
};

export default PlayerHand;
