import React from 'react';
import AuthLayout from '../components/AuthLayout';
import Link from 'next/link';

const HomePage: React.FC = () => {
  return (
    <AuthLayout
      title="Welcome to Card Game"
      description="A strategic card game where your decisions matter"
    >
      <div className="max-w-4xl mx-auto">
        {/* Hero section */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
          <div className="p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Start Your Card Game Journey
            </h2>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Collect cards, build powerful decks, and challenge other players in this strategic card game.
              Every decision matters as you climb the ranks and become a legendary player.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
              <Link href="/register" className="btn btn-primary">
                Create Account
              </Link>
              <Link href="/login" className="btn btn-outline text-primary-600 border-primary-600">
                Sign In
              </Link>
            </div>
          </div>
        </div>

        {/* Features section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex-center text-primary-600 dark:text-primary-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Collect Cards</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Build your collection with hundreds of unique cards, each with special abilities and strategies.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex-center text-primary-600 dark:text-primary-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Build Decks</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Create powerful deck combinations that match your playstyle and strategy.
            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <div className="w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-lg flex-center text-primary-600 dark:text-primary-400 mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Battle Players</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Challenge other players in real-time matches and climb the competitive ladder.
            </p>
          </div>
        </div>

        {/* Call to action */}
        <div className="bg-gradient-to-r from-primary-500 to-primary-700 rounded-lg shadow-md p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to Play?</h2>
          <p className="mb-6 max-w-2xl mx-auto">
            Join thousands of players already enjoying Card Game. Create your account now and receive a starter pack of cards!
          </p>
          <Link href="/register" className="btn bg-white text-primary-600 hover:bg-gray-100">
            Get Started
          </Link>
        </div>
      </div>
    </AuthLayout>
  );
};

export default HomePage;
