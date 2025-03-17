import React from 'react';
import { PlayerManagementProps } from '../types/game';
import PlayerSearch from './PlayerSearch';
import PlayerList from './PlayerList';

const PlayerManagement: React.FC<PlayerManagementProps> = ({
  gameId,
  currentPlayerId,
  players,
  onInvitePlayer,
  onRemovePlayer,
  onToggleReady,
}) => {
  const currentPlayer = players.find((p) => p.id === currentPlayerId);

  return (
    <div className="player-management">
      <div className="search-section">
        <h2>Invite Players</h2>
        <PlayerSearch
          onSelectPlayer={(player) => onInvitePlayer(player.id)}
          excludePlayerIds={players.map((p) => p.id)}
        />
      </div>

      <div className="players-section">
        <PlayerList
          players={players}
          currentPlayerId={currentPlayerId}
          onRemovePlayer={onRemovePlayer}
          showRemoveButton={true}
        />
      </div>

      <div className="ready-section">
        <button
          onClick={onToggleReady}
          className={`ready-button ${currentPlayer?.ready ? 'ready' : ''}`}
          aria-pressed={currentPlayer?.ready}
        >
          {currentPlayer?.ready ? 'Not Ready' : 'Ready'}
        </button>
      </div>

      <style jsx>{`
        .player-management {
          display: flex;
          flex-direction: column;
          gap: 2rem;
          padding: 1.5rem;
          max-width: 800px;
          margin: 0 auto;
        }

        .search-section,
        .players-section,
        .ready-section {
          width: 100%;
        }

        .search-section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #2d3748;
          margin-bottom: 1rem;
        }

        .ready-section {
          display: flex;
          justify-content: center;
        }

        .ready-button {
          padding: 0.75rem 2rem;
          font-size: 1rem;
          font-weight: 600;
          border-radius: 0.5rem;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
          background-color: #e2e8f0;
          color: #4a5568;
        }

        .ready-button:hover {
          background-color: #cbd5e0;
        }

        .ready-button.ready {
          background-color: #48bb78;
          color: white;
        }

        .ready-button.ready:hover {
          background-color: #38a169;
        }
      `}</style>
    </div>
  );
};

export default PlayerManagement;
