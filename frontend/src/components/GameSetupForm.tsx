import React from "react";

interface RuleSet {
  id: string;
  name: string;
  description: string;
  version: string;
}

interface GameSettings {
  gameType: string;
  maxPlayers: number;
  timeLimit?: number;
  useAI: boolean;
  ruleSetId: string;
}

interface GameSetupFormProps {
  settings: GameSettings;
  onChange: (settings: Partial<GameSettings>) => void;
  ruleSets: RuleSet[];
  loadingRuleSets: boolean;
}

const GameSetupForm: React.FC<GameSetupFormProps> = ({
  settings,
  onChange,
  ruleSets,
  loadingRuleSets
}) => {
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
      <div>
        <label htmlFor="ruleSetId" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Rule Set
        </label>
        {loadingRuleSets ? (
          <div className="animate-pulse bg-gray-200 dark:bg-gray-700 h-10 rounded-md w-full"></div>
        ) : (
          <>
            <select
              id="ruleSetId"
              name="ruleSetId"
              value={settings.ruleSetId}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
              data-testid="rule-set-select"
            >
              {ruleSets.length === 0 ? (
                <option value="">No rule sets available</option>
              ) : (
                ruleSets.map((ruleSet) => (
                  <option key={ruleSet.id} value={ruleSet.id}>
                    {ruleSet.name} (v{ruleSet.version})
                  </option>
                ))
              )}
            </select>
            {settings.ruleSetId && ruleSets.length > 0 && (
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                {ruleSets.find(rs => rs.id === settings.ruleSetId)?.description || "No description available."}
              </p>
            )}
          </>
        )}
      </div>

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
            data-testid="game-type-select"
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
            data-testid="max-players-input"
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
            Time Limit (minutes, 5-120, or 0 for no limit)
          </label>
          <input
            type="number"
            id="timeLimit"
            name="timeLimit"
            min="0"
            max="120"
            value={settings.timeLimit}
            onChange={(e) => {
              const value = parseInt(e.target.value, 10);
              // Allow 0 (no limit) or values between 5 and 120
              if (value === 0 || (value >= 5 && value <= 120)) {
                onChange({ timeLimit: value });
              } else if (value < 5 && value !== 0) {
                onChange({ timeLimit: 5 });
              } else if (value > 120) {
                onChange({ timeLimit: 120 });
              }
            }}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
            data-testid="time-limit-input"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Set to 0 for no time limit, or between 5-120 minutes.
          </p>
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
