import ApiService from '../../src/services/api';

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
  length: 0,
  key: jest.fn(),
};

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

describe('ApiService', () => {
  const mockGameId = 'game123';
  const mockToken = 'mock-jwt-token';
  const mockGameConfig = {
    game_type: 'standard' as const,
    max_players: 4,
    time_limit: 300,
    use_ai: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
    mockLocalStorage.getItem.mockReturnValue(mockToken);
  });

  describe('request handling', () => {
    it('includes authorization header when token exists', async () => {
      const mockResponse = { ok: true, json: () => Promise.resolve({ data: {} }) };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      await ApiService.getGameState(mockGameId);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
        })
      );
    });

    it('handles API errors correctly', async () => {
      const errorMessage = 'API Error';
      const mockResponse = {
        ok: false,
        json: () => Promise.resolve({ message: errorMessage }),
      };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await ApiService.getGameState(mockGameId);

      expect(result.error).toBe(errorMessage);
      expect(result.data).toBeNull();
    });
  });

  describe('game management', () => {
    it('creates a game successfully', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          game_id: mockGameId,
          status: 'waiting',
          players: [],
          current_player: '',
        }),
      };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await ApiService.createGame(mockGameConfig);

      expect(result.data).toEqual({
        game_id: mockGameId,
        status: 'waiting',
        players: [],
        current_player: '',
      });
    });

    it('joins a game successfully', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          game_id: mockGameId,
          status: 'waiting',
          players: ['player1'],
          current_player: 'player1',
        }),
      };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await ApiService.joinGame(mockGameId);

      expect(result.data).toEqual({
        game_id: mockGameId,
        status: 'waiting',
        players: ['player1'],
        current_player: 'player1',
      });
    });
  });

  describe('game actions', () => {
    const mockCard = { suit: 'hearts', value: '10' };

    it('plays a card successfully', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          effects: {
            next_player: 'player2',
            direction_changed: false,
            cards_drawn: 0,
            skipped: false,
          },
        }),
      };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await ApiService.playCard(mockGameId, mockCard);

      expect(result.data.success).toBe(true);
      expect(result.data.effects).toBeDefined();
    });

    it('draws a card successfully', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          card: mockCard,
        }),
      };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await ApiService.drawCard(mockGameId);

      expect(result.data.card).toEqual(mockCard);
    });

    it('announces one card successfully', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({ success: true }),
      };
      (global.fetch as jest.Mock).mockResolvedValueOnce(mockResponse);

      const result = await ApiService.announceOneCard(mockGameId);

      expect(result.data.success).toBe(true);
    });
  });

  describe('error detection', () => {
    it('correctly identifies API errors', () => {
      const errorResponse = { data: null, error: 'Test error' };
      const successResponse = { data: { success: true } };

      expect(ApiService.isApiError(errorResponse)).toBe(true);
      expect(ApiService.isApiError(successResponse)).toBe(false);
    });
  });
});
