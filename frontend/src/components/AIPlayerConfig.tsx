import React, { useState } from "react";

interface AIPlayer {
  id: string;
  difficulty: string;
}

interface AIPlayerConfigProps {
  maxAIPlayers: number;
}

const AIPlayerConfig: React.FC<AIPlayerConfigProps> = ({ maxAIPlayers }) => {
  const [aiPlayers, setAIPlayers] = useState<AIPlayer[]>([]);

  const handleAddAI = () => {
    if (aiPlayers.length >= maxAIPlayers) {
      return;
    }

    setAIPlayers([
      ...aiPlayers,
      {
        id: `ai-${Date.now()}`,
        difficulty: "medium",
      },
    ]);
  };

  const handleRemoveAI = (id: string) => {
    setAIPlayers(aiPlayers.filter((player) => player.id !== id));
  };

  const handleChangeDifficulty = (id: string, difficulty: string) => {
    setAIPlayers(
      aiPlayers.map((player) => (player.id === id ? { ...player, difficulty } : player))
    );
  };

  return (
    <div className="space-y-4">
      {maxAIPlayers <= 0 ? (
        <div className="bg-yellow-50 dark:bg-yellow-900 p-4 rounded-md">
          <p className="text-yellow-800 dark:text-yellow-200 text-sm">
            Maximum number of players reached. You cannot add AI players.
          </p>
        </div>
      ) : (
        <>
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              You can add up to {maxAIPlayers} AI players
            </p>
            <button
              onClick={handleAddAI}
              disabled={aiPlayers.length >= maxAIPlayers}
              className="px-3 py-1 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50 text-sm"
            >
              Add AI Player
            </button>
          </div>

          {aiPlayers.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-700 rounded-md p-4">
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">AI Players</h3>
              <ul className="divide-y divide-gray-200 dark:divide-gray-600">
                {aiPlayers.map((player, index) => (
                  <li key={player.id} className="py-3 flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="text-gray-800 dark:text-gray-200 mr-3">AI Player {index + 1}</span>
                      <select
                        value={player.difficulty}
                        onChange={(e) => handleChangeDifficulty(player.id, e.target.value)}
                        className="px-2 py-1 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white text-sm"
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
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {aiPlayers.length > 0 && (
            <div className="bg-blue-50 dark:bg-blue-900 p-4 rounded-md">
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
