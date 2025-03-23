import React, { useState, useCallback, useEffect } from 'react';
import { Player } from '../types/game';
import ApiService from '../services/api';
import debounce from 'lodash/debounce';

interface PlayerSearchProps {
  onSelectPlayer: (player: Player) => void;
  excludePlayerIds?: string[];
}

const PlayerSearch: React.FC<PlayerSearchProps> = ({ onSelectPlayer, excludePlayerIds = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<Player[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchPlayers = useCallback(
    debounce(async (term: string) => {
      if (!term.trim()) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await ApiService.searchPlayers(term);
        if (response.error) {
          throw new Error(response.error);
        }

        const filteredPlayers = response.data.players.filter(
          (player) => !excludePlayerIds.includes(player.id)
        );
        setResults(filteredPlayers);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to search players');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300),
    [excludePlayerIds]
  );

  useEffect(() => {
    searchPlayers(searchTerm);
    return () => {
      searchPlayers.cancel();
    };
  }, [searchTerm, searchPlayers]);

  return (
    <div className="player-search" role="search">
      <div className="search-input-container">
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="Search players..."
          aria-label="Search players"
          className="search-input"
        />
        {isLoading && <span className="loading-indicator">Searching...</span>}
      </div>

      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}

      <ul className="player-list" role="listbox">
        {results.map((player) => (
          <li
            key={player.id}
            role="option"
            aria-selected="false"
            className="player-item"
            onClick={() => onSelectPlayer(player)}
          >
            <div className="player-info">
              {player.avatar_url && (
                <img
                  src={player.avatar_url}
                  alt={`${player.name}'s avatar`}
                  className="player-avatar"
                />
              )}
              <span className="player-name">{player.name}</span>
            </div>
            <span className={`player-status status-${player.status}`}>
              {player.status}
            </span>
          </li>
        ))}
        {results.length === 0 && searchTerm && !isLoading && (
          <li className="no-results">No players found</li>
        )}
      </ul>

      <style jsx>{`
        .player-search {
          width: 100%;
          max-width: 400px;
          margin: 0 auto;
        }

        .search-input-container {
          position: relative;
          margin-bottom: 1rem;
        }

        .search-input {
          width: 100%;
          padding: 0.75rem;
          border: 2px solid #e2e8f0;
          border-radius: 0.5rem;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .search-input:focus {
          outline: none;
          border-color: #4a90e2;
        }

        .loading-indicator {
          position: absolute;
          right: 1rem;
          top: 50%;
          transform: translateY(-50%);
          color: #718096;
          font-size: 0.875rem;
        }

        .error-message {
          color: #e53e3e;
          padding: 0.5rem;
          margin-bottom: 1rem;
          border-radius: 0.25rem;
          background-color: #fff5f5;
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
          cursor: pointer;
          transition: background-color 0.2s;
          border-bottom: 1px solid #e2e8f0;
        }

        .player-item:last-child {
          border-bottom: none;
        }

        .player-item:hover {
          background-color: #f7fafc;
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

        .player-name {
          font-weight: 500;
          color: #2d3748;
        }

        .player-status {
          font-size: 0.875rem;
          padding: 0.25rem 0.5rem;
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

        .no-results {
          padding: 1rem;
          text-align: center;
          color: #718096;
        }
      `}</style>
    </div>
  );
};

export default PlayerSearch;
