import {
  GameConfig,
  Card,
  CardProps,
  PlayerState,
  GameState,
  WebSocketEvent,
  CardPlayedEvent,
  GameEndedEvent,
  GameAction,
} from '../../src/types/game';

describe('Game Types', () => {
  describe('GameConfig', () => {
    it('should create valid game config', () => {
      const config: GameConfig = {
        game_type: 'standard',
        max_players: 4,
        time_limit: 300,
        use_ai: false,
      };
      expect(config).toBeDefined();
      expect(config.game_type).toBe('standard');
    });
  });

  describe('Card and CardProps', () => {
    it('should create valid card', () => {
      const card: Card = {
        suit: 'hearts',
        value: '10',
        playable: true,
      };
      expect(card).toBeDefined();
    });

    it('should create valid card props', () => {
      const cardProps: CardProps = {
        card: { suit: 'hearts', value: '10' },
        onPlay: (card: Card) => {},
        isPlayable: true,
      };
      expect(cardProps).toBeDefined();
    });
  });

  describe('GameState', () => {
    it('should create valid game state', () => {
      const gameState: GameState = {
        currentPlayer: 'player1',
        nextPlayer: 'player2',
        direction: 'clockwise',
        playerStates: {
          player1: {
            hand: [],
            announcedOneCard: false,
            penalties: 0,
          },
        },
        discardPile: [],
        gameOver: false,
      };
      expect(gameState).toBeDefined();
    });
  });

  describe('WebSocket Events', () => {
    it('should create valid websocket event', () => {
      const event: WebSocketEvent = {
        type: 'card_played',
        data: { card: { suit: 'hearts', value: '10' } },
      };
      expect(event).toBeDefined();
    });

    it('should create valid card played event', () => {
      const event: CardPlayedEvent = {
        player_id: 'player1',
        card: {
          suit: 'hearts',
          rank: '10',
          value: 10,
        },
        effects: {
          next_player: 'player2',
          direction_changed: false,
          cards_drawn: 0,
          skipped: false,
        },
      };
      expect(event).toBeDefined();
    });

    it('should create valid game ended event', () => {
      const event: GameEndedEvent = {
        winner_id: 'player1',
        scores: {
          player1: 100,
          player2: 50,
        },
      };
      expect(event).toBeDefined();
    });
  });

  describe('Game Actions', () => {
    it('should create valid game actions', () => {
      const playCardAction: GameAction = {
        type: 'PLAY_CARD',
        payload: { suit: 'hearts', value: '10' },
      };
      expect(playCardAction).toBeDefined();

      const drawCardAction: GameAction = { type: 'DRAW_CARD' };
      expect(drawCardAction).toBeDefined();
    });
  });
});
