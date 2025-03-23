import * as auth from '../../src/utils/auth';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string): string | null => {
      return store[key] || null;
    },
    setItem: (key: string, value: string): void => {
      store[key] = value;
    },
    removeItem: (key: string): void => {
      delete store[key];
    },
    clear: (): void => {
      store = {};
    }
  };
})();

// Mock axios
jest.mock('axios', () => {
  return {
    default: {
      defaults: {
        headers: {
          common: {}
        }
      }
    }
  };
});

// Get the mocked axios
const mockedAxios = require('axios').default;

describe('Authentication Utilities', () => {
  beforeEach(() => {
    // Setup localStorage mock before each test
    Object.defineProperty(window, 'localStorage', { value: localStorageMock });
    localStorageMock.clear();

    // Reset axios headers
    mockedAxios.defaults.headers.common = {};
  });

  describe('Token Storage', () => {
    test('storeTokens should save tokens to localStorage', () => {
      // Arrange
      const accessToken = 'test-access-token';
      const refreshToken = 'test-refresh-token';

      // Act
      auth.storeTokens(accessToken, refreshToken);

      // Assert
      expect(localStorage.getItem('accessToken')).toBe(accessToken);
      expect(localStorage.getItem('refreshToken')).toBe(refreshToken);
    });

    test('getAccessToken should retrieve access token from localStorage', () => {
      // Arrange
      const accessToken = 'test-access-token';
      localStorage.setItem('accessToken', accessToken);

      // Act
      const result = auth.getAccessToken();

      // Assert
      expect(result).toBe(accessToken);
    });

    test('getAccessToken should return null if no token exists', () => {
      // Act
      const result = auth.getAccessToken();

      // Assert
      expect(result).toBeNull();
    });

    test('getRefreshToken should retrieve refresh token from localStorage', () => {
      // Arrange
      const refreshToken = 'test-refresh-token';
      localStorage.setItem('refreshToken', refreshToken);

      // Act
      const result = auth.getRefreshToken();

      // Assert
      expect(result).toBe(refreshToken);
    });

    test('getRefreshToken should return null if no token exists', () => {
      // Act
      const result = auth.getRefreshToken();

      // Assert
      expect(result).toBeNull();
    });

    test('clearTokens should remove tokens from localStorage', () => {
      // Arrange
      localStorage.setItem('accessToken', 'test-access-token');
      localStorage.setItem('refreshToken', 'test-refresh-token');

      // Act
      auth.clearTokens();

      // Assert
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });
  });

  describe('Authentication Status', () => {
    test('isAuthenticated should return true when access token exists', () => {
      // Arrange
      localStorage.setItem('accessToken', 'test-access-token');

      // Act
      const result = auth.isAuthenticated();

      // Assert
      expect(result).toBe(true);
    });

    test('isAuthenticated should return false when access token does not exist', () => {
      // Act
      const result = auth.isAuthenticated();

      // Assert
      expect(result).toBe(false);
    });
  });

  describe('Authorization Headers', () => {
    test('setAuthHeader should set Authorization header in axios', () => {
      // Arrange
      const token = 'test-token';

      // Act
      auth.setAuthHeader(token);

      // Assert
      expect(mockedAxios.defaults.headers.common['Authorization']).toBe(`Bearer ${token}`);
    });

    test('clearAuthHeader should remove Authorization header from axios', () => {
      // Arrange
      mockedAxios.defaults.headers.common['Authorization'] = 'Bearer test-token';

      // Act
      auth.clearAuthHeader();

      // Assert
      expect(mockedAxios.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });

  describe('Logout', () => {
    test('logout should clear tokens and authorization header', () => {
      // Arrange
      localStorage.setItem('accessToken', 'test-access-token');
      localStorage.setItem('refreshToken', 'test-refresh-token');
      mockedAxios.defaults.headers.common['Authorization'] = 'Bearer test-token';

      // Act
      auth.logout();

      // Assert
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
      expect(mockedAxios.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });
});
