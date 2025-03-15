import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";
import { getAccessToken, isAuthenticated } from "../../utils/auth";
import GameSetupForm from "../../components/GameSetupForm";
import PlayerInviteSection from "../../components/PlayerInviteSection";
import AIPlayerConfig from "../../components/AIPlayerConfig";

interface GameSettings {
  gameType: string;
  maxPlayers: number;
  timeLimit?: number;
  useAI: boolean;
}

const GameStartPage: React.FC = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [gameId, setGameId] = useState<string | null>(null);
  const [gameSettings, setGameSettings] = useState<GameSettings>({
    gameType: "standard",
    maxPlayers: 4,
    timeLimit: 45, // Default time limit of 45 minutes
    useAI: false,
  });
  const [invitedPlayers, setInvitedPlayers] = useState<Array<{ id: string; username: string; status: string }>>([]);

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push("/login");
      return;
    }
  }, [router]);

  const handleSettingsChange = (settings: Partial<GameSettings>) => {
    setGameSettings((prev) => ({ ...prev, ...settings }));
  };

  const handleCreateGame = async () => {
    setLoading(true);
    setError("");

    try {
      const accessToken = getAccessToken();
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games/`,
        {
          game_type: gameSettings.gameType,
          max_players: gameSettings.maxPlayers,
          time_limit: gameSettings.timeLimit,
          use_ai: gameSettings.useAI,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      console.log("Game creation response:", response.data);
      setGameId(response.data.game_uid);
      setLoading(false);
    } catch (error) {
      console.error("Error creating game:", error);

      // Extract the specific error message from the response if available
      let errorMessage = "Failed to create game. Please try again.";
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

  const handleInvitePlayer = async (playerId: string) => {
    if (!gameId) {
      setError("Please create a game first before inviting players.");
      return;
    }

    try {
      const accessToken = getAccessToken();
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games/${gameId}/invite/`,
        {
          player_uid: playerId,
        },
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      ).then(response => {
        console.log("Player invitation response:", response.data);

        // Update invited players list with actual data from response
        setInvitedPlayers((prev) => [
          ...prev,
          {
            id: playerId,
            username: response.data.username || "Player", // Use username from response if available
            status: response.data.status || "pending",
          },
        ]);
      });
    } catch (error) {
      console.error("Error inviting player:", error);

      // Extract the specific error message from the response if available
      let errorMessage = "Failed to invite player. Please try again.";
      if (axios.isAxiosError(error) && error.response) {
        // Check if the error response has a specific error message
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error;
        }
      }

      setError(errorMessage);
    }
  };

  const handleStartGame = async () => {
    if (!gameId) {
      setError("Please create a game first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const accessToken = getAccessToken();
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/api/games/${gameId}/start/`,
        {},
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      ).then(response => {
        console.log("Game start response:", response.data);

        // Redirect to the game page
        router.push(`/game/${gameId}`);
      });
    } catch (error) {
      console.error("Error starting game:", error);

      // Extract the specific error message from the response if available
      let errorMessage = "Failed to start game. Please try again.";
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

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Start New Game</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          {error && (
            <div className="mb-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          <div className="space-y-8">
            {/* Game Setup Form */}
            <section>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Game Settings</h2>
              <GameSetupForm settings={gameSettings} onChange={handleSettingsChange} />

              {!gameId && (
                <button
                  onClick={handleCreateGame}
                  disabled={loading}
                  className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700 disabled:opacity-50"
                >
                  {loading ? "Creating..." : "Create Game"}
                </button>
              )}
            </section>

            {/* Player Invite Section - Only show if game has been created */}
            {gameId && (
              <section>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Invite Players</h2>
                <PlayerInviteSection
                  invitedPlayers={invitedPlayers}
                  onInvitePlayer={handleInvitePlayer}
                  maxPlayers={gameSettings.maxPlayers}
                />
              </section>
            )}

            {/* AI Player Config - Only show if useAI is true and game has been created */}
            {gameSettings.useAI && gameId && (
              <section>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">AI Players</h2>
                <AIPlayerConfig
                  maxAIPlayers={gameSettings.maxPlayers - invitedPlayers.length - 1} // -1 for the current player
                  gameId={gameId}
                />
              </section>
            )}

            {/* Start Game Button - Only show if game has been created */}
            {gameId && (
              <section className="flex justify-end">
                <button
                  onClick={handleStartGame}
                  disabled={loading}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 text-lg font-medium"
                >
                  {loading ? "Starting..." : "Start Game"}
                </button>
              </section>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default GameStartPage;
