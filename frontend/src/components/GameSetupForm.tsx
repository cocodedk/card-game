import React from "react";

interface GameSettings {
  gameType: string;
  maxPlayers: number;
  timeLimit?: number;
  useAI: boolean;
}

interface GameSetupFormProps {
  settings: GameSettings;
  onChange: (settings: Partial<GameSettings>) => void;
}

const GameSetupForm: React.FC<GameSetupFormProps> = ({ settings, onChange }) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;

    if (type === "checkbox") {
      const checked = (e.target as HTMLInputElement).checked;
      onChange({ [name]: checked });
    } else if (type === "number") {
      onChange({ [name]: parseInt(value, 10) });
    } else {
      onChange({ [name]: value });
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="gameType" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Game Type
          </label>
          <select
            id="gameType"
            name="gameType"
            value={settings.gameType}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="standard">Standard Game</option>
            <option value="quick">Quick Game</option>
            <option value="tournament">Tournament</option>
          </select>
        </div>

        <div>
          <label htmlFor="maxPlayers" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Max Players
          </label>
          <select
            id="maxPlayers"
            name="maxPlayers"
            value={settings.maxPlayers}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
          >
            <option value={2}>2 Players</option>
            <option value={3}>3 Players</option>
            <option value={4}>4 Players</option>
            <option value={6}>6 Players</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="timeLimit" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Time Limit (minutes, 0 for no limit)
          </label>
          <input
            type="number"
            id="timeLimit"
            name="timeLimit"
            min="0"
            max="60"
            value={settings.timeLimit}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        <div className="flex items-center h-full pt-6">
          <input
            type="checkbox"
            id="useAI"
            name="useAI"
            checked={settings.useAI}
            onChange={handleChange}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label htmlFor="useAI" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
            Include AI Players
          </label>
        </div>
      </div>

      {settings.gameType === "tournament" && (
        <div className="bg-yellow-50 dark:bg-yellow-900 p-4 rounded-md mt-4">
          <p className="text-yellow-800 dark:text-yellow-200 text-sm">
            Tournament mode will create multiple rounds of games. Players will be matched based on their performance.
          </p>
        </div>
      )}
    </div>
  );
};

export default GameSetupForm;
