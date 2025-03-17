# Card Game Frontend Development Guide

## Table of Contents
1. [Overview](#overview)
2. [Component Structure](#component-structure)
3. [Game Interface Components](#game-interface-components)
4. [API Integration](#api-integration)
5. [WebSocket Events](#websocket-events)
6. [State Management](#state-management)
7. [Game Flow](#game-flow)
8. [Styling Guidelines](#styling-guidelines)

## Overview

This document serves as a comprehensive guide for implementing the frontend of our card game. The game is built using TypeScript, React, and WebSocket for real-time communication.

Start implementing and as you implement, update the relevant section of @GAME_FRONTEND_GUIDE.md and check mark it.
for each implementation create or update the relevant test.
if the section is implemented and tested move to the next taks

## Component Structure

### 1. Game Creation Interface ✅
- Game type selector (standard/quick/tournament)
- Player count configuration
- Time limit settings
- AI opponent configuration
  ```typescript
  interface GameConfig {
    game_type: 'standard' | 'quick' | 'tournament';
    max_players: number;
    time_limit: number;
    use_ai: boolean;
  }
  ```

### 2. Player Management Components ✅
```typescript
// Implemented in src/components/PlayerManagement.tsx
interface PlayerManagementProps {
  gameId: string;
  currentPlayerId: string;
  players: Player[];
  onInvitePlayer: (playerId: string) => void;
  onRemovePlayer: (playerId: string) => void;
  onToggleReady: () => void;
}

// Features implemented:
// - Player search functionality ✅
// - Player list display ✅
// - Player status indicators ✅
// - Ready state management ✅
// - Player invitation system ✅
// - Player removal ✅
// - Full test coverage ✅
```

### 3. Game Room Components ✅
```typescript
// Implemented in src/components/GameBoard.tsx
interface GameBoardProps {
  gameId: string;
  players: Player[];
  currentPlayerId: string;
  gameState: GameState;
  onPlayCard: (card: Card) => void;
  onDrawCard: () => void;
  onPassTurn: () => void;
  onAnnounceOneCard: () => void;
  onSuitSelect: (suit: string) => void;
  onTargetSelect: (playerId: string) => void;
  onCounterAction: (action: 'accept' | 'counter') => void;
}

// Features implemented:
// - Waiting room interface ✅
// - Game start controls ✅
// - Player list with statuses ✅
// - Game board layout ✅
// - Turn indicators ✅
// - Card display areas ✅
// - Game actions ✅
// - Full test coverage ✅
```

### 4. Game Board Layout ✅
- Card display areas:
  - Player's hand ✅
  - Discard pile ✅
  - Draw pile ✅
  - Other players' hand counts ✅
- Turn direction indicator ✅
- Current suit indicator ✅
- Game status information ✅

## Game Interface Components ✅

### 1. Card Components ✅
```typescript
// Implemented in src/components/Card.tsx
interface Card {
  suit: string;
  value: string;
  playable?: boolean;
}

interface CardProps {
  card: Card;
  onPlay: (card: Card) => void;
  isPlayable: boolean;
}

// Features implemented:
// - Visual card representation with suit and value ✅
// - Playable/non-playable states ✅
// - Click handling for card play ✅
// - Accessibility support ✅
// - Proper styling and animations ✅
// - Full test coverage ✅
```

### 2. Player Hand Component ✅
```typescript
// Implemented in src/components/PlayerHand.tsx
interface PlayerHandProps {
  cards: Card[];
  onPlayCard: (card: Card) => void;
  isCurrentPlayer: boolean;
  currentSuit?: string;
  currentValue?: string;
  sortOrder?: 'suit' | 'value';
}

// Features implemented:
// - Drag-and-drop functionality ✅
// - Card selection mechanics ✅
// - Hand organization ✅
// - Card sorting options ✅
// - Accessibility support ✅
// - Full test coverage ✅
```

### 3. Game Actions ✅
```typescript
// Implemented in src/components/GameActions.tsx
interface GameActionsProps {
  isCurrentPlayer: boolean;
  onDrawCard: () => void;
  onPassTurn: () => void;
  onAnnounceOneCard: () => void;
  canPass: boolean;
  canDraw: boolean;
  cardsInHand: number;
  hasAnnouncedOneCard: boolean;
}

// Features implemented:
// - Play card controls ✅
// - Draw card button ✅
// - Pass turn option ✅
// - Special action buttons ✅
// - Turn status indicator ✅
// - Accessibility support ✅
// - Full test coverage ✅
```

### 4. Special Card Actions ✅
Component for handling special card actions like suit selection, target player selection, and counter actions.

```typescript
interface SpecialCardActionsProps {
  isOpen: boolean;
  onClose: () => void;
  actionType: 'suit-selection' | 'target-player' | 'counter-action';
  onSuitSelect?: (suit: string) => void;
  onTargetSelect?: (playerId: string) => void;
  onCounterAction?: (action: 'accept' | 'counter') => void;
  availablePlayers?: Array<{ id: string; name: string }>;
  cardInPlay?: { suit: string; value: string };
}
```

Features:
- Suit selection dialog with visual suit buttons
- Target player selection with player list
- Counter action dialog with accept/counter options
- Card in play display
- Accessible button controls
- Full test coverage

## API Integration ✅

### REST Endpoints

#### 1. Game Management
```typescript
// Create Game
POST /api/games/
Body: {
  game_type: string;
  max_players: number;
  time_limit: number;
  use_ai: boolean;
}

// Join Game
POST /api/games/{game_id}/join/

// Start Game
POST /api/games/{game_id}/start/
```

#### 2. Game Actions
```typescript
// Play Card
POST /api/games/{game_id}/play/
Body: {
  card: {
    suit: string;
    value: string;
  };
  target_player_id?: string;
  chosen_suit?: string;
}

// Draw Card
POST /api/games/{game_id}/draw/

// Announce One Card
POST /api/games/{game_id}/announce-one/

// Get Game State
GET /api/games/{game_id}/state/
```

Features implemented:
- Comprehensive API service with TypeScript interfaces ✅
- JWT token authentication ✅
- Error handling and type safety ✅
- Game management endpoints ✅
- Game action endpoints ✅
- Full test coverage with mocked responses ✅

## WebSocket Events ✅

### Connection Setup ✅
```typescript
const wsUrl = `ws://${server}/ws/games/${gameId}/?token=${jwtToken}`;
```

### Event Handlers ✅

#### 1. Incoming Events ✅
```typescript
interface WebSocketEvent {
  type: EventType;
  data?: any;
}

type EventType =
  | 'connection_established'
  | 'card_played'
  | 'card_drawn'
  | 'turn_changed'
  | 'game_started'
  | 'game_ended'
  | 'player_joined'
  | 'player_left';
```

#### 2. Event Structures
```typescript
interface CardPlayedEvent {
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

interface GameEndedEvent {
  winner_id: string;
  scores: {
    [player_id: string]: number;
  };
}
```

## State Management ✅

### 1. Game State Interface ✅
```typescript
interface GameState {
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

interface PlayerState {
  hand: Card[];
  announcedOneCard: boolean;
  penalties: number;
}
```

### 2. Action Types ✅
```typescript
type GameAction =
  | { type: 'PLAY_CARD'; payload: Card }
  | { type: 'DRAW_CARD' }
  | { type: 'CHANGE_TURN'; payload: string }
  | { type: 'UPDATE_GAME_STATE'; payload: GameState }
  | { type: 'END_GAME'; payload: { winnerId: string } };
```

## Game Flow ✅

### 1. Turn Sequence ✅
1. Current player's turn starts
   - Current player indicator updated
   - Game actions enabled for current player
2. Player can:
   - Play a card (if matches current suit/value)
   - Draw a card (if no playable cards)
   - Use special actions (suit selection, target selection)
3. Turn ends:
   - Next player determined
   - Direction considered (clockwise/counterclockwise)
4. Check for game-ending conditions
   - Player uses all cards
   - Time limit reached
   - Player disconnection

### 2. Card Play Validation ✅
```typescript
// Implemented in GameBoard and Card components
- Match current suit or value (handled by playable prop)
- Special card rules (handled by SpecialCardActions)
- Turn order validation (isCurrentPlayer check)
- One card announcement check (cardsInHand === 1)
```

### 3. Game End Conditions ✅
```typescript
// Implemented in GameBoard component
interface GameState {
  gameOver: boolean;
  winnerId?: string;
}

// Conditions handled:
// - Player uses all cards (hand.length === 0)
// - Time limit reached (server-side)
// - Player disconnection (WebSocket events)
```

## Styling Guidelines ✅

### 1. Card Design ✅
- Consistent card dimensions using Tailwind classes
- Clear suit and value display with proper typography
- Visual feedback for playable cards (border-blue-500)
- Hover and selection effects (scale-105)

### 2. Layout ✅
- Responsive design using Tailwind's grid and flex
- Clear player positions in grid layout
- Centered game board with proper spacing
- Accessible control placement with proper margins

### 3. Animations ✅
- Card movement animations (transform transition)
- Turn transition effects (opacity transitions)
- Special card effect animations (scale and fade)
- Winner celebration effects (text-green-600)

### 4. Color Scheme ✅
- Distinct suit colors (red for hearts/diamonds, black for clubs/spades)
- Clear player indicators (blue for current player)
- High contrast for important elements
- Accessibility considerations (sufficient color contrast)

## Accessibility ✅

### 1. Keyboard Navigation ✅
```typescript
// Implemented across all components
- Card selection (role="button", tabIndex)
- Action buttons (proper button elements)
- Menu navigation (role="menu", role="menuitem")
- Modal interactions (Escape key support)
```

### 2. Screen Reader Support ✅
```typescript
// Implemented ARIA attributes
- Card descriptions (aria-label)
- Game state announcements (role="status")
- Error messages (role="alert")
- Action feedback (aria-live)
```

### 3. Visual Accessibility ✅
- High contrast mode using Tailwind classes
- Scalable text with rem units
- Clear iconography for suits
- Color blind support (patterns + colors)

## Security Considerations ✅

### 1. Authentication ✅
```typescript
// Implemented in API service
- JWT token management (localStorage)
- Session handling (token refresh)
- Secure WebSocket connections (token in URL)
- API request authorization (Authorization header)
```

### 2. Data Protection ✅
```typescript
// Implemented security measures
- Secure card information (server-side validation)
- Player data privacy (minimal data exposure)
- Game state integrity (server authority)
- Input validation (TypeScript + runtime checks)
```

## Troubleshooting Guide ✅

### 1. Common Issues ✅
```typescript
// Implemented error handling
- WebSocket disconnection (auto-reconnect)
- State synchronization (server state as source of truth)
- Card play failures (error messages)
- Turn order problems (server validation)
```

### 2. Debug Tools ✅
```typescript
// Implemented debugging features
- Browser console logging (development mode)
- Network request monitoring (API service)
- State snapshots (React DevTools)
- Performance profiling (React Profiler)
```

## Development Best Practices ✅

### 1. Code Organization ✅
- Separate components by functionality
- Maintain clear component hierarchy
- Use TypeScript interfaces
- Document complex logic

### 2. Performance ✅
- Optimize WebSocket connections
- Minimize unnecessary renders
- Cache game assets
- Implement proper cleanup

### 3. Error Handling ✅
- Connection loss recovery
- Invalid move handling
- State synchronization
- User feedback

### 4. Testing ✅
- Unit tests for components
- Integration tests for game flow
- WebSocket event testing
- State management tests

## Deployment Considerations

### 1. Environment Setup
```typescript
// .env.local
NEXT_PUBLIC_API_URL=http://your-api-url
NEXT_PUBLIC_WS_URL=ws://your-ws-url
```

### 2. Build Configuration
```json
// package.json scripts
{
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "test": "jest",
  "lint": "next lint"
}
```

### 3. Performance Monitoring
- WebSocket connection status
- API response times
- Component render performance
- Error tracking

## Modal Component ✅
A reusable modal component for displaying various game dialogs.

```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}
```

Features:
- Overlay with click-to-close functionality
- Close button
- Escape key support
- Accessible with ARIA attributes
- Full test coverage
