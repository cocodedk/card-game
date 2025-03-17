import React from 'react';
import { Card, GameState, Player } from '@/types/game';
import PlayerHand from './PlayerHand';
import GameActions from './GameActions';
import SpecialCardActions from './SpecialCardActions';

const suitSymbols = {
  hearts: '♥',
  diamonds: '♦',
  clubs: '♣',
  spades: '♠',
};

interface GameBoardProps {
  gameId: string;
  players: Player[];
  currentPlayerId: string;
  gameState: GameState;
  onPlayCard: (card: Card) => void;
  onDrawCard: () => void;
  onPassTurn: () => void;
  onAnnounceOneCard: () => void;
  onSuitSelect: (suit: string) => void;
  onTargetSelect: (playerId: string) => void;
  onCounterAction: (action: 'accept' | 'counter') => void;
}

const GameBoard: React.FC<GameBoardProps> = ({
  gameId,
  players,
  currentPlayerId,
  gameState,
  onPlayCard,
  onDrawCard,
  onPassTurn,
  onAnnounceOneCard,
  onSuitSelect,
  onTargetSelect,
  onCounterAction,
}) => {
  const currentPlayerState = gameState.playerStates[currentPlayerId];
  const isCurrentPlayer = gameState.currentPlayer === currentPlayerId;
  const currentPlayerName = players.find(p => p.id === gameState.currentPlayer)?.name;
  const nextPlayerName = players.find(p => p.id === gameState.nextPlayer)?.name;

  return (
    <div className="flex flex-col items-center gap-8 p-8">
      {/* Game Status */}
      <div className="flex flex-col items-center gap-2">
        <h2 className="text-2xl font-bold">Game Status</h2>
        <div className="flex gap-4">
          <span>Current Turn: {currentPlayerName}</span>
          <span>Next Turn: {nextPlayerName}</span>
          <span>Direction: {gameState.direction === 'clockwise' ? 'Clockwise' : 'Counterclockwise'}</span>
          {gameState.currentSuit && (
            <span>Current Suit: {gameState.currentSuit.charAt(0).toUpperCase() + gameState.currentSuit.slice(1)}</span>
          )}
        </div>
      </div>

      {/* Game Over State */}
      {gameState.gameOver && gameState.winnerId && (
        <div className="text-center">
          <h2 className="text-3xl font-bold text-green-600">Game Over!</h2>
          <p className="text-xl">
            Winner: {players.find(p => p.id === gameState.winnerId)?.name}
          </p>
        </div>
      )}

      {/* Discard Pile */}
      <div className="flex flex-col items-center gap-2">
        <h3 className="text-lg font-semibold">Discard Pile</h3>
        <div className="border border-gray-300 rounded-lg p-4">
          {gameState.discardPile.length > 0 && (
            <div className="text-2xl">
              <span data-testid="discard-value">{gameState.discardPile[0].value}</span>
              <span data-testid="discard-suit">{suitSymbols[gameState.discardPile[0].suit as keyof typeof suitSymbols]}</span>
            </div>
          )}
        </div>
      </div>

      {/* Player States */}
      <div className="grid grid-cols-3 gap-8 w-full">
        {players.map(player => {
          const playerState = gameState.playerStates[player.id];
          return (
            <div
              key={player.id}
              className={`p-4 border rounded-lg ${
                gameState.currentPlayer === player.id ? 'border-blue-500' : 'border-gray-300'
              }`}
            >
              <h3 className="font-semibold">
                {player.name} {player.id === currentPlayerId && '(You)'}
              </h3>
              <div className="text-sm text-gray-600">
                <p>Cards: {playerState.hand.length}</p>
                {playerState.penalties > 0 && <p>Penalties: {playerState.penalties}</p>}
                {playerState.announcedOneCard && <p className="text-yellow-600 font-bold">Has one card!</p>}
              </div>
            </div>
          );
        })}
      </div>

      {/* Player Hand */}
      <div className="w-full">
        <PlayerHand
          cards={currentPlayerState.hand}
          onPlayCard={onPlayCard}
          isCurrentPlayer={isCurrentPlayer}
          currentSuit={gameState.currentSuit}
          sortOrder="suit"
        />
      </div>

      {/* Game Actions */}
      <div className="flex flex-row gap-4 p-4 bg-gray-100 rounded-lg shadow-md" data-testid="game-actions">
        <button
          data-testid="draw-card-button"
          className={`
          px-4 py-2 rounded-lg font-medium transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2
         ${
           isCurrentPlayer
             ? 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
             : 'bg-blue-300 text-white cursor-not-allowed'
         }`}
          onClick={onDrawCard}
          disabled={!isCurrentPlayer}
        >
          Draw Card
        </button>
        <button
          data-testid="pass-turn-button"
          className={`
          px-4 py-2 rounded-lg font-medium transition-all duration-200
          focus:outline-none focus:ring-2 focus:ring-offset-2
         ${
           isCurrentPlayer
             ? 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500'
             : 'bg-gray-300 text-white cursor-not-allowed'
         }`}
          onClick={onPassTurn}
          disabled={!isCurrentPlayer}
        >
          Pass Turn
        </button>
        {currentPlayerState.hand.length === 1 && !currentPlayerState.announcedOneCard && (
          <button
            data-testid="announce-one-card-button"
            className={`
            px-4 py-2 rounded-lg font-medium transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-2
            bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500
          `}
            onClick={onAnnounceOneCard}
          >
            Announce One Card
          </button>
        )}
        <div className="flex items-center ml-4 text-sm text-gray-600" data-testid="turn-status">
          <span className={`font-medium ${isCurrentPlayer ? 'text-green-600' : 'text-gray-500'}`}>
            {isCurrentPlayer ? 'Your turn' : 'Waiting for other player'}
          </span>
        </div>
      </div>

      {/* Special Card Actions */}
      <SpecialCardActions
        isOpen={false}
        onClose={() => {}}
        actionType="suit-selection"
        onSuitSelect={onSuitSelect}
        onTargetSelect={onTargetSelect}
        onCounterAction={onCounterAction}
        availablePlayers={players}
      />
    </div>
  );
};

export default GameBoard;
