import React from 'react';
import { Player } from '../types/game';

interface PlayerListProps {
  players: Player[];
  currentPlayerId: string;
  onRemovePlayer?: (playerId: string) => void;
  showRemoveButton?: boolean;
}

const PlayerList: React.FC<PlayerListProps> = ({
  players,
  currentPlayerId,
  onRemovePlayer,
  showRemoveButton = false,
}) => {
  return (
    <div className="player-list-container">
      <h3 className="player-list-title">Players</h3>
      <ul className="player-list" role="list">
        {players.map((player) => (
          <li
            key={player.id}
            className={`player-item ${player.ready ? 'player-ready' : ''}`}
            role="listitem"
          >
            <div className="player-info">
              {player.avatar_url && (
                <img
                  src={player.avatar_url}
                  alt={`${player.name}'s avatar`}
                  className="player-avatar"
                />
              )}
              <div className="player-details">
                <span className="player-name">
                  {player.name}
                  {player.id === currentPlayerId && ' (You)'}
                </span>
                <span className={`player-status status-${player.status}`}>
                  {player.status}
                </span>
              </div>
            </div>
            <div className="player-actions">
              {player.ready && (
                <span className="ready-indicator" role="status">
                  Ready
                </span>
              )}
              {showRemoveButton && onRemovePlayer && player.id !== currentPlayerId && (
                <button
                  onClick={() => onRemovePlayer(player.id)}
                  className="remove-button"
                  aria-label={`Remove ${player.name}`}
                >
                  ✕
                </button>
              )}
            </div>
          </li>
        ))}
      </ul>

      <style jsx>{`
        .player-list-container {
          width: 100%;
          max-width: 400px;
          margin: 0 auto;
        }

        .player-list-title {
          font-size: 1.25rem;
          font-weight: 600;
          color: #2d3748;
          margin-bottom: 1rem;
        }

        .player-list {
          list-style: none;
          padding: 0;
          margin: 0;
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          overflow: hidden;
        }

        .player-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem 1rem;
          border-bottom: 1px solid #e2e8f0;
          background-color: white;
          transition: background-color 0.2s;
        }

        .player-item:last-child {
          border-bottom: none;
        }

        .player-item.player-ready {
          background-color: #f0fff4;
        }

        .player-info {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .player-avatar {
          width: 2rem;
          height: 2rem;
          border-radius: 50%;
          object-fit: cover;
        }

        .player-details {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }

        .player-name {
          font-weight: 500;
          color: #2d3748;
        }

        .player-status {
          font-size: 0.75rem;
          padding: 0.125rem 0.375rem;
          border-radius: 1rem;
          text-transform: capitalize;
        }

        .status-online {
          background-color: #c6f6d5;
          color: #22543d;
        }

        .status-offline {
          background-color: #e2e8f0;
          color: #4a5568;
        }

        .status-in_game {
          background-color: #bee3f8;
          color: #2c5282;
        }

        .player-actions {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }

        .ready-indicator {
          font-size: 0.75rem;
          padding: 0.125rem 0.375rem;
          background-color: #c6f6d5;
          color: #22543d;
          border-radius: 1rem;
        }

        .remove-button {
          background: none;
          border: none;
          color: #e53e3e;
          cursor: pointer;
          padding: 0.25rem;
          font-size: 1rem;
          line-height: 1;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background-color 0.2s;
        }

        .remove-button:hover {
          background-color: #fff5f5;
        }

        .remove-button:focus {
          outline: none;
          box-shadow: 0 0 0 2px #fed7d7;
        }
      `}</style>
    </div>
  );
};

export default PlayerList;
