import React, { useState, useEffect } from "react";
import axios from "axios";
import { getAccessToken } from "../utils/auth";

interface AIPlayer {
  id: string;
  difficulty: string;
}

interface AIPlayerConfigProps {
  maxAIPlayers: number;
  gameId: string;
}

const AIPlayerConfig: React.FC<AIPlayerConfigProps> = ({ maxAIPlayers, gameId }) => {
  const [aiPlayers, setAIPlayers] = useState<AIPlayer[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAddAI = async () => {
    if (aiPlayers.length >= maxAIPlayers) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      const difficulty = "medium"; // Default difficulty
      const accessToken = getAccessToken();

      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games/${gameId}/add_ai/`,
        {
          difficulty: difficulty
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      // Generate a unique ID for the AI player since the backend doesn't return one
      const aiPlayerId = `ai-${Date.now()}`;

      // Add the new AI player to the list
      setAIPlayers([
        ...aiPlayers,
        {
          id: aiPlayerId,
          difficulty: response.data.difficulty || difficulty,
        },
      ]);

      setLoading(false);
    } catch (error) {
      console.error("Error adding AI player:", error);

      // Extract the specific error message from the response if available
      let errorMessage = "Failed to add AI player. Please try again.";
      if (axios.isAxiosError(error) && error.response) {
        // Check if the error response has a specific error message
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        }
      }

      setError(errorMessage);
      setLoading(false);
    }
  };

  const handleRemoveAI = (id: string) => {
    // In a real implementation, we would call an API to remove the AI player
    // For now, we'll just update the local state
    setAIPlayers(aiPlayers.filter((player) => player.id !== id));
  };

  const handleChangeDifficulty = (id: string, difficulty: string) => {
    // In a real implementation, we would call an API to update the AI player's difficulty
    // For now, we'll just update the local state
    setAIPlayers(
      aiPlayers.map((player) => (player.id === id ? { ...player, difficulty } : player))
    );
  };

  return (
    <div className="space-y-4" data-testid="ai-player-config">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert" data-testid="ai-error-message">
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      {maxAIPlayers <= 0 ? (
        <div className="bg-yellow-50 dark:bg-yellow-900 p-4 rounded-md" data-testid="ai-max-players-warning">
          <p className="text-yellow-800 dark:text-yellow-200 text-sm">
            Maximum number of players reached. You cannot add AI players.
          </p>
        </div>
      ) : (
        <>
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-700 dark:text-gray-300" data-testid="ai-players-info">
              You can add up to {maxAIPlayers} AI players
            </p>
            <button
              onClick={handleAddAI}
              disabled={loading || aiPlayers.length >= maxAIPlayers}
              className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50 text-sm"
              data-testid="add-ai-button"
            >
              {loading ? "Adding..." : "Add AI Player"}
            </button>
          </div>

          {aiPlayers.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4" data-testid="ai-players-list">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">AI Players</h3>
              <ul className="divide-y divide-gray-200 dark:divide-gray-600">
                {aiPlayers.map((player, index) => (
                  <li key={player.id} className="py-3 flex items-center justify-between" data-testid={`ai-player-${index}`}>
                    <div className="flex items-center">
                      <span className="text-gray-800 dark:text-gray-200 mr-3">AI Player {index + 1}</span>
                      <select
                        value={player.difficulty}
                        onChange={(e) => handleChangeDifficulty(player.id, e.target.value)}
                        className="px-2 py-1 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white text-sm"
                        data-testid={`ai-difficulty-select-${index}`}
                      >
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                        <option value="expert">Expert</option>
                      </select>
                    </div>
                    <button
                      onClick={() => handleRemoveAI(player.id)}
                      className="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-xs"
                      data-testid={`remove-ai-button-${index}`}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {aiPlayers.length > 0 && (
            <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-md" data-testid="difficulty-info">
              <p className="text-blue-800 dark:text-blue-200 text-sm">
                <span className="font-medium">Difficulty levels:</span>
                <br />
                <span className="block mt-1">
                  <strong>Easy:</strong> Makes basic moves, suitable for beginners.
                </span>
                <span className="block">
                  <strong>Medium:</strong> Makes strategic moves, challenging for casual players.
                </span>
                <span className="block">
                  <strong>Hard:</strong> Makes advanced strategic moves, challenging for experienced players.
                </span>
                <span className="block">
                  <strong>Expert:</strong> Makes optimal moves, extremely challenging.
                </span>
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AIPlayerConfig;
