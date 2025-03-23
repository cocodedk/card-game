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
  PlayerHandProps,
  SortedHand,
  GameActionsProps,
  SpecialCardActionsProps,
  ModalProps,
  Player,
  PlayerSearchResult,
  InvitationStatus,
  PlayerManagementProps
} from '../../src/types/game';

describe('Game Types', () => {
  describe('Card Types', () => {
    it('should create a valid Card object', () => {
      const card: Card = {
        suit: 'hearts',
        value: '10',
        playable: true
      };

      expect(card.suit).toBe('hearts');
      expect(card.value).toBe('10');
      expect(card.playable).toBe(true);
    });

    it('should create a valid CardProps object', () => {
      const card: Card = {
        suit: 'clubs',
        value: 'A'
      };

      const onPlay = jest.fn();

      const cardProps: CardProps = {
        card,
        onPlay,
        isPlayable: true
      };

      expect(cardProps.card).toEqual(card);
      expect(cardProps.onPlay).toBe(onPlay);
      expect(cardProps.isPlayable).toBe(true);

      // Test the callback
      cardProps.onPlay(card);
      expect(onPlay).toHaveBeenCalledWith(card);
    });
  });

  describe('Game Configuration Types', () => {
    it('should create a valid GameConfig object', () => {
      const config: GameConfig = {
        game_type: 'standard',
        max_players: 4,
        time_limit: 30,
        use_ai: false
      };

      expect(config.game_type).toBe('standard');
      expect(config.max_players).toBe(4);
      expect(config.time_limit).toBe(30);
      expect(config.use_ai).toBe(false);
    });

    it('should accept different game types', () => {
      const standardConfig: GameConfig = {
        game_type: 'standard',
        max_players: 4,
        time_limit: 30,
        use_ai: false
      };

      const quickConfig: GameConfig = {
        game_type: 'quick',
        max_players: 2,
        time_limit: 10,
        use_ai: true
      };

      const tournamentConfig: GameConfig = {
        game_type: 'tournament',
        max_players: 8,
        time_limit: 60,
        use_ai: false
      };

      expect(standardConfig.game_type).toBe('standard');
      expect(quickConfig.game_type).toBe('quick');
      expect(tournamentConfig.game_type).toBe('tournament');
    });
  });

  describe('Game State Types', () => {
    it('should create a valid PlayerState object', () => {
      const playerState: PlayerState = {
        hand: [
          { suit: 'hearts', value: '2' },
          { suit: 'diamonds', value: 'K' }
        ],
        announcedOneCard: false,
        penalties: 0
      };

      expect(playerState.hand.length).toBe(2);
      expect(playerState.announcedOneCard).toBe(false);
      expect(playerState.penalties).toBe(0);
    });

    it('should create a valid GameState object', () => {
      const gameState: GameState = {
        currentPlayer: 'player1',
        nextPlayer: 'player2',
        direction: 'clockwise',
        playerStates: {
          player1: {
            hand: [{ suit: 'hearts', value: 'A' }],
            announcedOneCard: false,
            penalties: 0
          },
          player2: {
            hand: [{ suit: 'spades', value: '7' }],
            announcedOneCard: true,
            penalties: 1
          }
        },
        discardPile: [
          { suit: 'diamonds', value: '3' }
        ],
        currentSuit: 'diamonds',
        gameOver: false
      };

      expect(gameState.currentPlayer).toBe('player1');
      expect(gameState.direction).toBe('clockwise');
      expect(gameState.playerStates.player1.hand.length).toBe(1);
      expect(gameState.playerStates.player2.announcedOneCard).toBe(true);
      expect(gameState.discardPile.length).toBe(1);
      expect(gameState.currentSuit).toBe('diamonds');
      expect(gameState.gameOver).toBe(false);
      expect(gameState.winnerId).toBeUndefined();
    });
  });

  describe('WebSocket Event Types', () => {
    it('should create a valid WebSocketEvent', () => {
      const event: WebSocketEvent = {
        type: 'card_played',
        data: { card: { suit: 'clubs', value: '4' } }
      };

      expect(event.type).toBe('card_played');
      expect(event.data.card.suit).toBe('clubs');
    });

    it('should handle all EventType values', () => {
      const events: EventType[] = [
        'connection_established',
        'card_played',
        'card_drawn',
        'turn_changed',
        'game_started',
        'game_ended',
        'player_joined',
        'player_left'
      ];

      events.forEach(eventType => {
        const event: WebSocketEvent = { type: eventType };
        expect(event.type).toBe(eventType);
      });
    });

    it('should create a valid CardPlayedEvent', () => {
      const cardPlayedEvent: CardPlayedEvent = {
        player_id: 'player1',
        card: {
          suit: 'hearts',
          rank: 'queen',
          value: 12
        },
        effects: {
          next_player: 'player3',
          direction_changed: true,
          cards_drawn: 2,
          skipped: false
        }
      };

      expect(cardPlayedEvent.player_id).toBe('player1');
      expect(cardPlayedEvent.card.suit).toBe('hearts');
      expect(cardPlayedEvent.effects.direction_changed).toBe(true);
    });

    it('should create a valid GameEndedEvent', () => {
      const gameEndedEvent: GameEndedEvent = {
        winner_id: 'player2',
        scores: {
          player1: 15,
          player2: 0,
          player3: 22
        }
      };

      expect(gameEndedEvent.winner_id).toBe('player2');
      expect(gameEndedEvent.scores.player2).toBe(0);
    });
  });

  describe('Game Action Types', () => {
    it('should create valid GameAction objects', () => {
      const playCardAction: GameAction = {
        type: 'PLAY_CARD',
        payload: { suit: 'spades', value: 'J' }
      };

      const drawCardAction: GameAction = {
        type: 'DRAW_CARD'
      };

      const changeTurnAction: GameAction = {
        type: 'CHANGE_TURN',
        payload: 'player3'
      };

      const updateGameStateAction: GameAction = {
        type: 'UPDATE_GAME_STATE',
        payload: {
          currentPlayer: 'player1',
          nextPlayer: 'player2',
          direction: 'clockwise',
          playerStates: {},
          discardPile: [],
          gameOver: false
        }
      };

      const endGameAction: GameAction = {
        type: 'END_GAME',
        payload: { winnerId: 'player1' }
      };

      expect(playCardAction.type).toBe('PLAY_CARD');
      expect(drawCardAction.type).toBe('DRAW_CARD');
      expect(changeTurnAction.type).toBe('CHANGE_TURN');
      expect(updateGameStateAction.type).toBe('UPDATE_GAME_STATE');
      expect(endGameAction.type).toBe('END_GAME');

      // Check payload types
      if (playCardAction.type === 'PLAY_CARD') {
        expect(playCardAction.payload.suit).toBe('spades');
      }

      if (changeTurnAction.type === 'CHANGE_TURN') {
        expect(changeTurnAction.payload).toBe('player3');
      }

      if (endGameAction.type === 'END_GAME') {
        expect(endGameAction.payload.winnerId).toBe('player1');
      }
    });
  });

  describe('Component Props Types', () => {
    it('should create valid PlayerHandProps', () => {
      const onPlayCard = jest.fn();

      const playerHandProps: PlayerHandProps = {
        cards: [{ suit: 'clubs', value: '2' }],
        onPlayCard,
        isCurrentPlayer: true,
        currentSuit: 'clubs',
        currentValue: '2',
        sortOrder: 'suit'
      };

      expect(playerHandProps.cards.length).toBe(1);
      expect(playerHandProps.isCurrentPlayer).toBe(true);
      expect(playerHandProps.sortOrder).toBe('suit');

      // Test callback
      playerHandProps.onPlayCard(playerHandProps.cards[0]);
      expect(onPlayCard).toHaveBeenCalledWith(playerHandProps.cards[0]);
    });

    it('should create a valid SortedHand object', () => {
      const sortedHand: SortedHand = {
        hearts: [
          { suit: 'hearts', value: '2' },
          { suit: 'hearts', value: 'K' }
        ],
        diamonds: [
          { suit: 'diamonds', value: '10' }
        ]
      };

      expect(sortedHand.hearts.length).toBe(2);
      expect(sortedHand.diamonds.length).toBe(1);
      expect(sortedHand.hearts[1].value).toBe('K');
    });

    it('should create valid GameActionsProps', () => {
      const onDrawCard = jest.fn();
      const onPassTurn = jest.fn();
      const onAnnounceOneCard = jest.fn();

      const gameActionsProps: GameActionsProps = {
        isCurrentPlayer: true,
        onDrawCard,
        onPassTurn,
        onAnnounceOneCard,
        canPass: true,
        canDraw: true,
        cardsInHand: 3,
        hasAnnouncedOneCard: false
      };

      expect(gameActionsProps.isCurrentPlayer).toBe(true);
      expect(gameActionsProps.canPass).toBe(true);
      expect(gameActionsProps.cardsInHand).toBe(3);

      // Test callbacks
      gameActionsProps.onDrawCard();
      expect(onDrawCard).toHaveBeenCalled();

      gameActionsProps.onPassTurn();
      expect(onPassTurn).toHaveBeenCalled();
    });

    it('should create valid SpecialCardActionsProps', () => {
      const onClose = jest.fn();
      const onSuitSelect = jest.fn();
      const onTargetSelect = jest.fn();
      const onCounterAction = jest.fn();

      const specialCardActionsProps: SpecialCardActionsProps = {
        isOpen: true,
        onClose,
        actionType: 'suit-selection',
        onSuitSelect,
        onTargetSelect,
        onCounterAction,
        availablePlayers: [
          { id: 'player1', name: 'John' },
          { id: 'player2', name: 'Lisa' }
        ],
        cardInPlay: { suit: 'hearts', value: 'Q' }
      };

      expect(specialCardActionsProps.isOpen).toBe(true);
      expect(specialCardActionsProps.actionType).toBe('suit-selection');
      expect(specialCardActionsProps.availablePlayers?.length).toBe(2);

      // Test callbacks
      specialCardActionsProps.onClose();
      expect(onClose).toHaveBeenCalled();

      if (specialCardActionsProps.onSuitSelect) {
        specialCardActionsProps.onSuitSelect('diamonds');
        expect(onSuitSelect).toHaveBeenCalledWith('diamonds');
      }
    });

    it('should create valid ModalProps', () => {
      const onClose = jest.fn();

      const modalProps: ModalProps = {
        isOpen: true,
        onClose,
        title: 'Test Modal',
        children: 'Test Content',
        className: 'custom-modal'
      };

      expect(modalProps.isOpen).toBe(true);
      expect(modalProps.title).toBe('Test Modal');
      expect(modalProps.className).toBe('custom-modal');

      // Test callback
      modalProps.onClose();
      expect(onClose).toHaveBeenCalled();
    });
  });

  describe('Player Types', () => {
    it('should create a valid Player object', () => {
      const player: Player = {
        id: 'player1',
        name: 'John Doe',
        status: 'online',
        ready: true,
        avatar_url: 'https://example.com/avatar.jpg'
      };

      expect(player.id).toBe('player1');
      expect(player.name).toBe('John Doe');
      expect(player.status).toBe('online');
      expect(player.ready).toBe(true);
    });

    it('should handle different player status values', () => {
      const onlinePlayer: Player = {
        id: 'p1',
        name: 'Online Player',
        status: 'online',
        ready: false
      };

      const offlinePlayer: Player = {
        id: 'p2',
        name: 'Offline Player',
        status: 'offline',
        ready: false
      };

      const inGamePlayer: Player = {
        id: 'p3',
        name: 'In Game Player',
        status: 'in_game',
        ready: true
      };

      expect(onlinePlayer.status).toBe('online');
      expect(offlinePlayer.status).toBe('offline');
      expect(inGamePlayer.status).toBe('in_game');
    });

    it('should create a valid PlayerSearchResult', () => {
      const searchResult: PlayerSearchResult = {
        players: [
          { id: 'p1', name: 'Player 1', status: 'online', ready: false },
          { id: 'p2', name: 'Player 2', status: 'offline', ready: false }
        ],
        total_count: 2
      };

      expect(searchResult.players.length).toBe(2);
      expect(searchResult.total_count).toBe(2);
    });

    it('should create a valid InvitationStatus', () => {
      const invitation: InvitationStatus = {
        id: 'inv1',
        from: { id: 'p1', name: 'Player 1', status: 'online', ready: true },
        to: { id: 'p2', name: 'Player 2', status: 'online', ready: false },
        game_id: 'game1',
        status: 'pending',
        created_at: '2023-03-23T12:34:56Z'
      };

      expect(invitation.id).toBe('inv1');
      expect(invitation.from.name).toBe('Player 1');
      expect(invitation.to.name).toBe('Player 2');
      expect(invitation.status).toBe('pending');
    });

    it('should create valid PlayerManagementProps', () => {
      const onInvitePlayer = jest.fn();
      const onRemovePlayer = jest.fn();
      const onToggleReady = jest.fn();

      const playerManagementProps: PlayerManagementProps = {
        gameId: 'game1',
        currentPlayerId: 'player1',
        players: [
          { id: 'player1', name: 'Current Player', status: 'online', ready: false },
          { id: 'player2', name: 'Other Player', status: 'online', ready: true }
        ],
        onInvitePlayer,
        onRemovePlayer,
        onToggleReady
      };

      expect(playerManagementProps.gameId).toBe('game1');
      expect(playerManagementProps.currentPlayerId).toBe('player1');
      expect(playerManagementProps.players.length).toBe(2);

      // Test callbacks
      playerManagementProps.onInvitePlayer('player3');
      expect(onInvitePlayer).toHaveBeenCalledWith('player3');

      playerManagementProps.onRemovePlayer('player2');
      expect(onRemovePlayer).toHaveBeenCalledWith('player2');

      playerManagementProps.onToggleReady();
      expect(onToggleReady).toHaveBeenCalled();
    });
  });
});
