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

  const shouldShowAnnounceOneCard = isCurrentPlayer && cardsInHand === 2 && !hasAnnouncedOneCard;

  return (
    <div
      className="flex flex-row gap-4 p-4 bg-gray-100 rounded-lg shadow-md"
      data-testid="game-actions"
    >
      {renderActionButton(
        'Draw Card',
        onDrawCard,
        isCurrentPlayer && canDraw,
        'draw-card-button',
        'primary'
      )}

      {renderActionButton(
        'Pass Turn',
        onPassTurn,
        isCurrentPlayer && canPass,
        'pass-turn-button',
        'secondary'
      )}

      {shouldShowAnnounceOneCard && renderActionButton(
        'Announce One Card!',
        onAnnounceOneCard,
        true,
        'announce-one-card-button',
        'warning'
      )}

      <div
        className="flex items-center ml-4 text-sm text-gray-600"
        data-testid="turn-status"
      >
        {isCurrentPlayer ? (
          <span className="font-medium text-green-600">Your turn</span>
        ) : (
          <span>Waiting for other player</span>
        )}
      </div>
    </div>
  );
};

export default GameActions;
