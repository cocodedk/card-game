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
      <div
        className="flex flex-col items-center gap-2"
        data-testid="game-status"
      >
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
        <div
          className="text-center"
          data-testid="winner-display"
        >
          <h2 className="text-3xl font-bold text-green-600">Game Over!</h2>
          <p className="text-xl">
            Winner: {players.find(p => p.id === gameState.winnerId)?.name}
          </p>
        </div>
      )}

      {/* Discard Pile */}
      <div className="flex flex-col items-center gap-2">
        <h3 className="text-lg font-semibold">Discard Pile</h3>
        <div
          className="border border-gray-300 rounded-lg p-4"
          data-testid="discard-pile"
        >
          {gameState.discardPile.length > 0 && (
            <div className="text-2xl">
              <span data-testid="discard-value">{gameState.discardPile[0].value}</span>
              <span data-testid="discard-suit">{suitSymbols[gameState.discardPile[0].suit as keyof typeof suitSymbols]}</span>
            </div>
          )}
        </div>
      </div>

      {/* Player States */}
      <div
        className="grid grid-cols-3 gap-8 w-full"
        data-testid="player-list"
      >
        {players.map((player) => (
          <div
            key={player.id}
            className={`p-4 border rounded-lg ${
              player.id === gameState.currentPlayer ? 'border-blue-500' : 'border-gray-300'
            }`}
            data-testid="player-status"
          >
            <h3 className="font-semibold">
              {player.name} {player.id === currentPlayerId && '(You)'}
            </h3>
            <div className="text-sm text-gray-600">
              <p>Cards: {gameState.playerStates[player.id]?.hand.length || 0}</p>
              {gameState.playerStates[player.id]?.announcedOneCard && (
                <p className="text-yellow-600">Has one card!</p>
              )}
              {gameState.playerStates[player.id]?.penalties > 0 && (
                <p className="text-red-600">
                  Penalties: {gameState.playerStates[player.id].penalties}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Player Hand */}
      <div className="w-full">
        <PlayerHand
          cards={gameState.playerStates[currentPlayerId]?.hand || []}
          onPlayCard={onPlayCard}
          isCurrentPlayer={currentPlayerId === gameState.currentPlayer}
          currentSuit={gameState.currentSuit}
          currentValue={gameState.discardPile[0]?.value}
        />
      </div>

      {/* Game Actions */}
      <GameActions
        isCurrentPlayer={currentPlayerId === gameState.currentPlayer}
        onDrawCard={onDrawCard}
        onPassTurn={onPassTurn}
        onAnnounceOneCard={onAnnounceOneCard}
        canPass={true}
        canDraw={true}
        cardsInHand={(gameState.playerStates[currentPlayerId]?.hand || []).length}
        hasAnnouncedOneCard={gameState.playerStates[currentPlayerId]?.announcedOneCard || false}
      />

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
