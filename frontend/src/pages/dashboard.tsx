import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";
import { getAccessToken, getRefreshToken, clearTokens, clearAuthHeader, isAuthenticated } from "../utils/auth";

const Dashboard: React.FC = () => {
  const router = useRouter();
  const [playerData, setPlayerData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      router.push('/login');
      return;
    }

    const fetchPlayerData = async () => {
      try {
        // Get player profile data with authorization header
        const accessToken = getAccessToken();
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL}/api/players/profile/`, {
          headers: {
            Authorization: `Bearer ${accessToken}`
          }
        });
        setPlayerData(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching player data:', error);

        // Handle different types of errors
        if (axios.isAxiosError(error)) {
          if (error.response?.status === 401) {
            console.log('Unauthorized access, redirecting to login');
            clearTokens();
            // Add a small delay before redirecting to ensure the error state is set
            setTimeout(() => {
              router.push('/login');
            }, 100);
          } else if (error.response?.status === 500) {
            // Handle server errors
            setError(`Server error: The server encountered an issue processing your request. Please try again later or contact support if the problem persists.`);
            console.error('Server error details:', error.response?.data);
          } else {
            // Handle other API errors
            const errorMessage = error.response?.data?.detail ||
                               error.response?.data?.message ||
                               'Unknown error';
            setError(`Failed to load player data: ${errorMessage}`);
          }
        } else {
          setError('Failed to load player data. Please try logging in again.');
        }
        setLoading(false);
      }
    };

    fetchPlayerData();
  }, [router]);

  const handleLogout = async () => {
    try {
      const refreshToken = getRefreshToken();

      // Only attempt to call logout API if we have a refresh token
      if (refreshToken) {
        try {
          await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/api/players/logout/`, {
            refresh: refreshToken
          }, {
            headers: {
              Authorization: `Bearer ${getAccessToken()}`
            }
          });
        } catch (logoutError) {
          // If logout API fails, just log the error but continue with local logout
          console.error('Error calling logout API:', logoutError);
        }
      }

      // Always clear tokens and auth header
      clearTokens();
      clearAuthHeader();

      router.push('/login');
    } catch (error) {
      console.error('Error logging out:', error);
      setError('Failed to log out. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen bg-gray-100 dark:bg-gray-900">
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md max-w-md w-full">
          <h2 className="text-xl text-red-600 dark:text-red-400 mb-4">Error</h2>
          <p className="text-gray-700 dark:text-gray-300 mb-4">{error}</p>
          <div className="flex space-x-4">
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
            >
              Retry
            </button>
            <button
              onClick={() => {
                clearTokens();
                router.push('/login');
              }}
              className="px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700"
            >
              Back to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Player Dashboard</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Welcome, {playerData?.callsign || playerData?.username || 'Player'}</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Player Profile</h3>
              <div className="space-y-2">
                <p className="text-gray-700 dark:text-gray-300"><span className="font-medium">Username:</span> {playerData?.username || 'Not available'}</p>
                <p className="text-gray-700 dark:text-gray-300"><span className="font-medium">Callsign:</span> {playerData?.callsign || 'Not set'}</p>
                <p className="text-gray-700 dark:text-gray-300"><span className="font-medium">Email:</span> {playerData?.email || 'Not available'}</p>
                {playerData?.first_name && (
                  <p className="text-gray-700 dark:text-gray-300">
                    <span className="font-medium">Name:</span> {playerData.first_name} {playerData?.last_name || ''}
                  </p>
                )}
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Game Statistics</h3>
              <div className="space-y-2">
                <p className="text-gray-700 dark:text-gray-300"><span className="font-medium">Games Played:</span> {playerData?.games_played || 0}</p>
                <p className="text-gray-700 dark:text-gray-300"><span className="font-medium">Wins:</span> {playerData?.wins || 0}</p>
                <p className="text-gray-700 dark:text-gray-300"><span className="font-medium">Losses:</span> {playerData?.losses || 0}</p>
                <p className="text-gray-700 dark:text-gray-300">
                  <span className="font-medium">Win Rate:</span> {
                    playerData?.games_played
                      ? `${((playerData?.wins / playerData?.games_played) * 100).toFixed(1)}%`
                      : 'N/A'
                  }
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Available Actions</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <button className="btn-primary p-4 flex flex-col items-center justify-center">
                <span className="text-lg mb-1">Find Game</span>
                <span className="text-sm">Join an existing game</span>
              </button>
              <button className="btn-secondary p-4 flex flex-col items-center justify-center">
                <span className="text-lg mb-1">Create Game</span>
                <span className="text-sm">Start a new game</span>
              </button>
              <button className="btn-outline p-4 flex flex-col items-center justify-center">
                <span className="text-lg mb-1">Edit Profile</span>
                <span className="text-sm">Update your information</span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
