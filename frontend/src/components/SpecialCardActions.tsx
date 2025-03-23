import React from 'react';
import { SpecialCardActionsProps } from '../types/game';
import Modal from './Modal';

const SpecialCardActions: React.FC<SpecialCardActionsProps> = ({
  isOpen,
  onClose,
  actionType,
  onSuitSelect,
  onTargetSelect,
  onCounterAction,
  availablePlayers,
  cardInPlay,
}) => {
  const handleSuitSelect = (suit: string) => {
    onSuitSelect?.(suit);
    onClose?.();
  };

  const handleTargetSelect = (playerId: string) => {
    onTargetSelect?.(playerId);
    onClose?.();
  };

  const handleCounterAction = (action: 'accept' | 'counter') => {
    onCounterAction?.(action);
    onClose?.();
  };

  const renderSuitSelection = () => (
    <div className="grid grid-cols-2 gap-4" data-testid="suit-selection">
      {['hearts', 'diamonds', 'clubs', 'spades'].map((suit) => (
        <button
          key={suit}
          onClick={() => handleSuitSelect(suit)}
          className="p-4 border rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          data-testid={`suit-${suit}`}
        >
          <span className={suit === 'hearts' || suit === 'diamonds' ? 'text-red-600' : 'text-gray-900'}>
            {suit === 'hearts' ? '♥' : suit === 'diamonds' ? '♦' : suit === 'clubs' ? '♣' : '♠'}
          </span>
          <span className="ml-2 capitalize">{suit}</span>
        </button>
      ))}
    </div>
  );

  const renderTargetSelection = () => (
    <div className="space-y-2" data-testid="target-selection">
      {availablePlayers?.map((player) => (
        <button
          key={player.id}
          onClick={() => handleTargetSelect(player.id)}
          className="w-full p-3 text-left border rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          data-testid={`player-${player.id}`}
        >
          {player.name}
        </button>
      ))}
    </div>
  );

  const renderCounterAction = () => (
    <div className="space-y-4" data-testid="counter-action">
      <div className="text-center mb-4">
        <p className="text-lg font-medium">
          {cardInPlay?.value} of {cardInPlay?.suit} was played
        </p>
        <p className="text-sm text-gray-600">Do you want to counter this card?</p>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => handleCounterAction('accept')}
          className="p-3 border rounded-lg bg-green-500 text-white hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500"
          data-testid="accept-action"
        >
          Accept
        </button>
        <button
          onClick={() => handleCounterAction('counter')}
          className="p-3 border rounded-lg bg-red-500 text-white hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500"
          data-testid="counter-action-button"
        >
          Counter
        </button>
      </div>
    </div>
  );

  const getModalContent = () => {
    switch (actionType) {
      case 'suit-selection':
        return {
          title: 'Select a Suit',
          content: renderSuitSelection(),
        };
      case 'target-player':
        return {
          title: 'Select a Target Player',
          content: renderTargetSelection(),
        };
      case 'counter-action':
        return {
          title: 'Counter Action Required',
          content: renderCounterAction(),
        };
      default:
        return {
          title: '',
          content: null,
        };
    }
  };

  const { title, content } = getModalContent();

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
    >
      {content}
    </Modal>
  );
};

export default SpecialCardActions;
