import React from 'react';
import { GameActionsProps } from '../types/game';

const GameActions: React.FC<GameActionsProps> = ({
  isCurrentPlayer,
  onDrawCard,
  onPassTurn,
  onAnnounceOneCard,
  canPass,
  canDraw,
  cardsInHand,
  hasAnnouncedOneCard,
}) => {
  const renderActionButton = (
    label: string,
    onClick: () => void,
    isEnabled: boolean,
    testId: string,
    variant: 'primary' | 'secondary' | 'warning' = 'primary'
  ) => {
    const baseClasses = `
      px-4 py-2 rounded-lg font-medium transition-all duration-200
      focus:outline-none focus:ring-2 focus:ring-offset-2
    `;

    const variantClasses = {
      primary: `
        bg-blue-600 text-white
        hover:bg-blue-700
        focus:ring-blue-500
        disabled:bg-blue-300
      `,
      secondary: `
        bg-gray-600 text-white
        hover:bg-gray-700
        focus:ring-gray-500
        disabled:bg-gray-300
      `,
      warning: `
        bg-yellow-600 text-white
        hover:bg-yellow-700
        focus:ring-yellow-500
        disabled:bg-yellow-300
      `,
    };

    return (
      <button
        onClick={onClick}
        disabled={!isEnabled}
        className={`${baseClasses} ${variantClasses[variant]}`}
        data-testid={testId}
        aria-disabled={!isEnabled}
      >
        {label}
      </button>
    );
  };

  const canAnnounceOneCard = isCurrentPlayer && cardsInHand === 1 && !hasAnnouncedOneCard;

  return (
    <div
      className="flex flex-row gap-4 p-4 bg-gray-100 rounded-lg shadow-md"
      data-testid="game-actions"
    >
      <button
        data-testid="draw-card-button"
        className={`
          px-4 py-2 rounded-lg font-medium transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2
          ${
            isCurrentPlayer && canDraw
              ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
              : 'bg-blue-300 text-white cursor-not-allowed'
          }
        `}
        onClick={onDrawCard}
        disabled={!isCurrentPlayer || !canDraw}
      >
        Draw Card
      </button>
      <button
        data-testid="pass-turn-button"
        className={`
          px-4 py-2 rounded-lg font-medium transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2
          ${
            isCurrentPlayer && canPass
              ? 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500'
              : 'bg-gray-300 text-white cursor-not-allowed'
          }
        `}
        onClick={onPassTurn}
        disabled={!isCurrentPlayer || !canPass}
      >
        Pass Turn
      </button>
      <button
        data-testid="announce-one-card-button"
        className={`
          px-4 py-2 rounded-lg font-medium transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2
          ${
            canAnnounceOneCard
              ? 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500'
              : 'bg-yellow-300 text-white cursor-not-allowed'
          }
        `}
        onClick={onAnnounceOneCard}
        disabled={!canAnnounceOneCard}
      >
        Announce One Card
      </button>
      <div
        className="flex items-center ml-4 text-sm text-gray-600"
        data-testid="turn-status"
      >
        <span className={`font-medium ${isCurrentPlayer ? 'text-green-600' : 'text-red-600'}`}>
          {isCurrentPlayer ? 'Your turn' : 'Waiting for turn'}
        </span>
      </div>
    </div>
  );
};

export default GameActions;
