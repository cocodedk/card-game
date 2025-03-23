// Mock dependencies before imports
jest.mock('@/styles/globals.css', () => ({}), { virtual: true });

import React from 'react';
import { render, screen } from '@testing-library/react';
import * as auth from '../../src/utils/auth';
import axios from 'axios';

// Import App after mocking dependencies
import App from '../../src/pages/_app';

// Mock dependencies
jest.mock('axios');
const mockAxios = axios as jest.Mocked<typeof axios>;

// Mock auth utilities
jest.mock('../../src/utils/auth', () => ({
  getAccessToken: jest.fn(),
  getRefreshToken: jest.fn(),
  storeTokens: jest.fn(),
  clearTokens: jest.fn(),
  setAuthHeader: jest.fn(),
}));

// Create a component that renders its children to track ReactQueryDevtools
const DevToolsTracker = jest.fn(({ children }: { children: React.ReactNode }) => <>{children}</>);

// Mock ReactQueryDevtools
jest.mock('@tanstack/react-query-devtools', () => ({
  ReactQueryDevtools: () => <div data-testid="react-query-devtools">DevTools</div>,
}));

// Mock process.env
const originalEnv = process.env;
beforeEach(() => {
  process.env = {
    ...originalEnv,
    NODE_ENV: 'test',
    NEXT_PUBLIC_API_URL: 'http://backend:8000',
  };
});

afterEach(() => {
  process.env = originalEnv;
});

// Mock a simple component to pass as Component
const MockComponent = ({ testId = 'test-component' }: { testId?: string }) => (
  <div data-testid={testId}>Test Component</div>
);

// Reset mocks before each test
beforeEach(() => {
  jest.clearAllMocks();

  // Reset axios interceptors - use any type to avoid TypeScript errors with mocks
  if (!mockAxios.interceptors) {
    (mockAxios as any).interceptors = {
      request: { use: jest.fn().mockReturnThis() },
      response: { use: jest.fn().mockReturnThis() },
    };
  } else {
    mockAxios.interceptors.request.use = jest.fn().mockReturnThis();
    mockAxios.interceptors.response.use = jest.fn().mockReturnThis();
  }

  // Set default mock for axios - use any type to avoid TypeScript errors
  (mockAxios as any).defaults = {
    withCredentials: false,
    headers: { common: {} }
  };

  // Mock window.location
  Object.defineProperty(window, 'location', {
    writable: true,
    value: { href: '' },
  });
});

describe('App Component', () => {
  test('renders the component passed as prop', () => {
    render(
      <App
        Component={MockComponent}
        pageProps={{ testId: 'custom-test-id' }}
        router={{} as any}
      />
    );

    const renderedComponent = screen.getByTestId('custom-test-id');
    expect(renderedComponent).toBeInTheDocument();
    expect(renderedComponent.textContent).toBe('Test Component');
  });

  test('sets up axios defaults and interceptors', () => {
    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Check axios defaults are set
    expect(mockAxios.defaults.withCredentials).toBe(true);

    // Check interceptors are added
    expect(mockAxios.interceptors.request.use).toHaveBeenCalled();
    expect(mockAxios.interceptors.response.use).toHaveBeenCalled();
  });

  test('sets auth header if access token exists', () => {
    // Mock access token
    (auth.getAccessToken as jest.Mock).mockReturnValue('test-access-token');

    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Check if setAuthHeader was called with the token
    expect(auth.setAuthHeader).toHaveBeenCalledWith('test-access-token');
  });

  test('does not set auth header if no access token exists', () => {
    // Mock no access token
    (auth.getAccessToken as jest.Mock).mockReturnValue(null);

    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Check if setAuthHeader was not called
    expect(auth.setAuthHeader).not.toHaveBeenCalled();
  });

  test('shows ReactQueryDevtools in development environment', () => {
    // Set environment to development
    process.env.NODE_ENV = 'development';

    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Check if ReactQueryDevtools is rendered using the data-testid
    expect(screen.getByTestId('react-query-devtools')).toBeInTheDocument();
  });

  test('does not show ReactQueryDevtools in production environment', () => {
    // Set environment to production
    process.env.NODE_ENV = 'production';

    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Check if ReactQueryDevtools is not rendered
    expect(screen.queryByTestId('react-query-devtools')).not.toBeInTheDocument();
  });
});

// Test the request interceptor
describe('Axios Request Interceptor', () => {
  test('adds Authorization header to requests if token exists', () => {
    // Mock access token
    (auth.getAccessToken as jest.Mock).mockReturnValue('test-access-token');

    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Get the request interceptor function
    const requestInterceptor = mockAxios.interceptors.request.use.mock.calls[0][0];

    // Create a mock config
    const config = { headers: {} };

    // Call the interceptor with the config
    const result = requestInterceptor(config);

    // Check if the Authorization header was added
    expect(result.headers.Authorization).toBe('Bearer test-access-token');
  });

  test('does not add Authorization header if no token exists', () => {
    // Mock no access token
    (auth.getAccessToken as jest.Mock).mockReturnValue(null);

    render(
      <App
        Component={MockComponent}
        pageProps={{}}
        router={{} as any}
      />
    );

    // Get the request interceptor function
    const requestInterceptor = mockAxios.interceptors.request.use.mock.calls[0][0];

    // Create a mock config
    const config = { headers: {} };

    // Call the interceptor with the config
    const result = requestInterceptor(config);

    // Check if the Authorization header was not added
    expect(result.headers.Authorization).toBeUndefined();
  });
});

// Note: Testing the response interceptor is more complex due to async behavior and would require
// more advanced mocking techniques. We've covered the basic functionality in these tests.
