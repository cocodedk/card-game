import React, { useState, useEffect } from "react";
import axios from "axios";
import { getAccessToken } from "../utils/auth";

interface Player {
  id: string;
  username: string;
  status: string;
}

interface PlayerInviteSectionProps {
  invitedPlayers: Player[];
  onInvitePlayer: (playerId: string) => void;
  maxPlayers: number;
}

const PlayerInviteSection: React.FC<PlayerInviteSectionProps> = ({
  invitedPlayers,
  onInvitePlayer,
  maxPlayers,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState<Array<{ id: string; username: string }>>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Calculate how many more players can be invited
  const remainingSlots = maxPlayers - invitedPlayers.length - 1; // -1 for the current player

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const accessToken = getAccessToken();
      const response = await axios.get(
        `${process.env.NEXT_PUBLIC_API_URL}/api/players/search/?query=${encodeURIComponent(searchTerm)}`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      // Filter out already invited players
      const filteredResults = response.data.filter(
        (player: { id: string }) => !invitedPlayers.some((invited) => invited.id === player.id)
      );

      setSearchResults(filteredResults);
      setLoading(false);
    } catch (error) {
      console.error("Error searching players:", error);
      setError("Failed to search players. Please try again.");
      setLoading(false);
    }
  };

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm) {
        handleSearch();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  return (
    <div className="space-y-6">
      {remainingSlots <= 0 ? (
        <div className="bg-yellow-50 dark:bg-yellow-900 p-4 rounded-md">
          <p className="text-yellow-800 dark:text-yellow-200 text-sm">
            Maximum number of players reached. You cannot invite more players.
          </p>
        </div>
      ) : (
        <>
          <div>
            <label htmlFor="playerSearch" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search Players
            </label>
            <div className="flex">
              <input
                type="text"
                id="playerSearch"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Enter username or email"
                className="flex-grow px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-l-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              />
              <button
                onClick={handleSearch}
                disabled={loading || !searchTerm.trim()}
                className="px-4 py-2 bg-primary-600 text-white rounded-r-md hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? "..." : "Search"}
              </button>
            </div>
            {error && <p className="mt-1 text-sm text-red-600 dark:text-red-400">{error}</p>}
          </div>

          {searchResults.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Results</h3>
              <ul className="divide-y divide-gray-200 dark:divide-gray-600">
                {searchResults.map((player) => (
                  <li key={player.id} className="py-2 flex justify-between items-center">
                    <span className="text-gray-800 dark:text-gray-200">{player.username}</span>
                    <button
                      onClick={() => onInvitePlayer(player.id)}
                      className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 text-sm"
                    >
                      Invite
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}

      {invitedPlayers.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Invited Players</h3>
          <ul className="divide-y divide-gray-200 dark:divide-gray-600 bg-gray-50 dark:bg-gray-700 rounded-md p-4">
            {invitedPlayers.map((player) => (
              <li key={player.id} className="py-2 flex justify-between items-center">
                <span className="text-gray-800 dark:text-gray-200">{player.username}</span>
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    player.status === "accepted"
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : player.status === "declined"
                      ? "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                      : "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                  }`}
                >
                  {player.status.charAt(0).toUpperCase() + player.status.slice(1)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default PlayerInviteSection;
