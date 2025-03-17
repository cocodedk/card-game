import { GameConfig, Card, PlayerSearchResult } from '../types/game';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ApiResponse<T> {
  data: T;
  error?: string;
}

interface GameResponse {
  game_id: string;
  status: 'waiting' | 'in_progress' | 'completed';
  players: string[];
  current_player: string;
}

interface GameStateResponse {
  game_id: string;
  current_player: string;
  next_player: string;
  direction: 'clockwise' | 'counterclockwise';
  players: {
    [key: string]: {
      cards_count: number;
      announced_one_card: boolean;
      penalties: number;
    };
  };
  discard_pile_top?: Card;
  current_suit?: string;
  game_over: boolean;
  winner_id?: string;
}

interface PlayCardResponse {
  success: boolean;
  effects?: {
    next_player: string;
    direction_changed: boolean;
    cards_drawn: number;
    skipped: boolean;
  };
}

class ApiService {
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const token = localStorage.getItem('jwt_token');
      const headers = {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'API request failed');
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        data: null as any,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  // Game Management
  static async createGame(config: GameConfig): Promise<ApiResponse<GameResponse>> {
    return this.request<GameResponse>('/games/', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  static async joinGame(gameId: string): Promise<ApiResponse<GameResponse>> {
    return this.request<GameResponse>(`/games/${gameId}/join/`, {
      method: 'POST',
    });
  }

  static async startGame(gameId: string): Promise<ApiResponse<GameResponse>> {
    return this.request<GameResponse>(`/games/${gameId}/start/`, {
      method: 'POST',
    });
  }

  // Game Actions
  static async playCard(
    gameId: string,
    card: Card,
    targetPlayerId?: string,
    chosenSuit?: string
  ): Promise<ApiResponse<PlayCardResponse>> {
    return this.request<PlayCardResponse>(`/games/${gameId}/play/`, {
      method: 'POST',
      body: JSON.stringify({
        card,
        target_player_id: targetPlayerId,
        chosen_suit: chosenSuit,
      }),
    });
  }

  static async drawCard(gameId: string): Promise<ApiResponse<{ card: Card }>> {
    return this.request<{ card: Card }>(`/games/${gameId}/draw/`, {
      method: 'POST',
    });
  }

  static async announceOneCard(gameId: string): Promise<ApiResponse<{ success: boolean }>> {
    return this.request<{ success: boolean }>(`/games/${gameId}/announce-one/`, {
      method: 'POST',
    });
  }

  static async getGameState(gameId: string): Promise<ApiResponse<GameStateResponse>> {
    return this.request<GameStateResponse>(`/games/${gameId}/state/`);
  }

  // Player Management
  static async searchPlayers(searchTerm: string): Promise<ApiResponse<PlayerSearchResult>> {
    return this.request<PlayerSearchResult>(`/players/search/?q=${encodeURIComponent(searchTerm)}`);
  }

  // Error Handling
  static isApiError(response: ApiResponse<any>): response is { error: string; data: null } {
    return response.error !== undefined;
  }
}

export default ApiService;
