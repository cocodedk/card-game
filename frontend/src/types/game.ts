// Game configuration types
export interface GameConfig {
  game_type: 'standard' | 'quick' | 'tournament';
  max_players: number;
  time_limit: number;
  use_ai: boolean;
}

// Card related types
export interface Card {
  suit: string;
  value: string;
  playable?: boolean;
}

export interface CardProps {
  card: Card;
  onPlay: (card: Card) => void;
  isPlayable: boolean;
}

// Game state types
export interface PlayerState {
  hand: Card[];
  announcedOneCard: boolean;
  penalties: number;
}

export interface GameState {
  currentPlayer: string;
  nextPlayer: string;
  direction: 'clockwise' | 'counterclockwise';
  playerStates: {
    [playerId: string]: PlayerState;
  };
  discardPile: Card[];
  currentSuit?: string;
  gameOver: boolean;
  winnerId?: string;
}

// WebSocket event types
export type EventType =
  | 'connection_established'
  | 'card_played'
  | 'card_drawn'
  | 'turn_changed'
  | 'game_started'
  | 'game_ended'
  | 'player_joined'
  | 'player_left';

export interface WebSocketEvent {
  type: EventType;
  data?: any;
}

export interface CardPlayedEvent {
  player_id: string;
  card: {
    suit: string;
    rank: string;
    value: number;
  };
  effects: {
    next_player: string;
    direction_changed: boolean;
    cards_drawn: number;
    skipped: boolean;
  };
}

export interface GameEndedEvent {
  winner_id: string;
  scores: {
    [player_id: string]: number;
  };
}

// Game actions
export type GameAction =
  | { type: 'PLAY_CARD'; payload: Card }
  | { type: 'DRAW_CARD' }
  | { type: 'CHANGE_TURN'; payload: string }
  | { type: 'UPDATE_GAME_STATE'; payload: GameState }
  | { type: 'END_GAME'; payload: { winnerId: string } };

// Player Hand types
export interface PlayerHandProps {
  cards: Card[];
  onPlayCard: (card: Card) => void;
  isCurrentPlayer: boolean;
  currentSuit?: string;
  currentValue?: string;
  sortOrder?: 'suit' | 'value';
}

export interface SortedHand {
  [key: string]: Card[];
}

// Game Actions types
export interface GameActionsProps {
  isCurrentPlayer: boolean;
  onDrawCard: () => void;
  onPassTurn: () => void;
  onAnnounceOneCard: () => void;
  canPass: boolean;
  canDraw: boolean;
  cardsInHand: number;
  hasAnnouncedOneCard: boolean;
}

// Special Card Actions types
export interface SpecialCardActionsProps {
  isOpen: boolean;
  onClose: () => void;
  actionType: 'suit-selection' | 'target-player' | 'counter-action';
  onSuitSelect?: (suit: string) => void;
  onTargetSelect?: (playerId: string) => void;
  onCounterAction?: (action: 'accept' | 'counter') => void;
  availablePlayers?: Array<{
    id: string;
    name: string;
  }>;
  cardInPlay?: Card;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  className?: string;
}

export interface Player {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'in_game';
  ready: boolean;
  avatar_url?: string;
}

export interface PlayerSearchResult {
  players: Player[];
  total_count: number;
}

export interface InvitationStatus {
  id: string;
  from: Player;
  to: Player;
  game_id: string;
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  created_at: string;
}

export interface PlayerManagementProps {
  gameId: string;
  currentPlayerId: string;
  players: Player[];
  onInvitePlayer: (playerId: string) => void;
  onRemovePlayer: (playerId: string) => void;
  onToggleReady: () => void;
}
