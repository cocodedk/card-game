import React, { ReactNode } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import Image from 'next/image';

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  description?: string;
  showLoginLink?: boolean;
  showRegisterLink?: boolean;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({
  children,
  title,
  description = 'Welcome to the Card Game',
  showLoginLink = true,
  showRegisterLink = true,
}) => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <Head>
        <title>{`${title} - Card Game`}</title>
        <meta name="description" content={description} />
      </Head>

      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="container-custom py-4">
          <div className="flex-between">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-primary-600 rounded-full flex-center text-white font-bold text-xl">
                CG
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">Card Game</span>
            </Link>

            <nav className="flex items-center space-x-6">
              <Link href="/" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                Home
              </Link>
              {showLoginLink && (
                <Link href="/login" className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white">
                  Login
                </Link>
              )}
              {showRegisterLink && (
                <Link href="/register" className="btn btn-primary">
                  Register
                </Link>
              )}
            </nav>
          </div>
        </div>
      </header>

      <main className="py-12">
        <div className="container-custom">
          <div className="text-center mb-8 animate-fade-in">
            <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
              {title}
            </h1>
            {description && (
              <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400 sm:mt-4">
                {description}
              </p>
            )}
          </div>

          <div className="animate-slide-in-up">
            {children}
          </div>
        </div>
      </main>

      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-8">
        <div className="container-custom">
          <div className="flex flex-col md:flex-row md:justify-between items-center">
            <div className="mb-4 md:mb-0">
              <p className="text-gray-500 dark:text-gray-400">
                &copy; {new Date().getFullYear()} Card Game. All rights reserved.
              </p>
            </div>
            <div className="flex space-x-6">
              <a href="#" className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                Terms
              </a>
              <a href="#" className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                Privacy
              </a>
              <a href="#" className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                Contact
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default AuthLayout;
