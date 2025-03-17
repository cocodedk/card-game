import { v4 as uuidv4 } from 'uuid';

describe('Complete Game Flow', () => {
  // Test users for our game
  const users = [
    { username: 'player1', password: 'testpass1' },
    { username: 'player2', password: 'testpass2' },
    { username: 'player3', password: 'testpass3' },
  ];

  const gameConfig = {
    game_type: 'standard',
    max_players: 3,
    time_limit: 300, // 5 minutes
    use_ai: false,
  };

  // Store tokens and game ID for use across tests
  let tokens: { [key: string]: string } = {};
  let gameId: string;

  before(() => {
    // Register and login all test users
    cy.wrap(users).each((user) => {
      cy.request('POST', `${Cypress.env('API_URL')}/auth/register`, user);
      cy.request('POST', `${Cypress.env('API_URL')}/auth/login`, user)
        .then((response) => {
          tokens[user.username] = response.body.token;
        });
    });
  });

  it('Player1 creates a game', () => {
    cy.visit('/');
    cy.get('[data-testid="login-username"]').type(users[0].username);
    cy.get('[data-testid="login-password"]').type(users[0].password);
    cy.get('[data-testid="login-submit"]').click();

    // Create game
    cy.get('[data-testid="create-game-button"]').click();
    cy.get('[data-testid="game-type-select"]').select(gameConfig.game_type);
    cy.get('[data-testid="max-players-input"]').type(gameConfig.max_players.toString());
    cy.get('[data-testid="time-limit-input"]').type(gameConfig.time_limit.toString());
    cy.get('[data-testid="create-game-submit"]').click();

    // Store game ID from URL
    cy.url().should('include', '/game/').then((url) => {
      gameId = url.split('/').pop() || '';
    });

    // Wait for game creation confirmation
    cy.get('[data-testid="game-status"]').should('contain', 'Waiting for players');
  });

  it('Other players join the game', () => {
    // Player 2 joins
    cy.visit(`/game/${gameId}`);
    cy.get('[data-testid="login-username"]').type(users[1].username);
    cy.get('[data-testid="login-password"]').type(users[1].password);
    cy.get('[data-testid="login-submit"]').click();
    cy.get('[data-testid="join-game-button"]').click();
    cy.get('[data-testid="player-ready-button"]').click();

    // Player 3 joins
    cy.visit(`/game/${gameId}`);
    cy.get('[data-testid="login-username"]').type(users[2].username);
    cy.get('[data-testid="login-password"]').type(users[2].password);
    cy.get('[data-testid="login-submit"]').click();
    cy.get('[data-testid="join-game-button"]').click();
    cy.get('[data-testid="player-ready-button"]').click();

    // Back to Player 1 to start the game
    cy.visit(`/game/${gameId}`);
    cy.get('[data-testid="login-username"]').type(users[0].username);
    cy.get('[data-testid="login-password"]').type(users[0].password);
    cy.get('[data-testid="login-submit"]').click();
    cy.get('[data-testid="player-ready-button"]').click();

    // Verify all players are ready
    cy.get('[data-testid="player-status"]').should('have.length', 3)
      .each(($el) => {
        cy.wrap($el).should('contain', 'Ready');
      });

    // Start game
    cy.get('[data-testid="start-game-button"]').click();
    cy.get('[data-testid="game-status"]').should('contain', 'Game in progress');
  });

  it('Players take turns and play cards', () => {
    // Helper function to play a turn
    const playTurn = (playerIndex: number) => {
      cy.visit(`/game/${gameId}`);
      cy.get('[data-testid="login-username"]').type(users[playerIndex].username);
      cy.get('[data-testid="login-password"]').type(users[playerIndex].password);
      cy.get('[data-testid="login-submit"]').click();

      // Wait for player's turn
      cy.get('[data-testid="turn-status"]').should('contain', 'Your turn');

      // Try to play a card or draw
      cy.get('[data-testid="player-hand"]').then(($hand) => {
        const playableCards = $hand.find('[data-testid="card"][aria-disabled="false"]');
        if (playableCards.length > 0) {
          cy.wrap(playableCards.first()).click();
        } else {
          cy.get('[data-testid="draw-card-button"]').click();
          // Try to play the drawn card
          cy.get('[data-testid="pass-turn-button"]').click();
        }
      });

      // Handle special card actions if they appear
      cy.get('body').then(($body) => {
        if ($body.find('[data-testid="suit-selection"]').length > 0) {
          cy.get('[data-testid="suit-hearts"]').click();
        }
        if ($body.find('[data-testid="target-selection"]').length > 0) {
          cy.get('[data-testid="target-player"]').first().click();
        }
      });
    };

    // Play several rounds
    for (let round = 0; round < 5; round++) {
      users.forEach((_, index) => {
        playTurn(index);
      });
    }
  });

  it('Game ends with a winner', () => {
    // Wait for game over state
    cy.get('[data-testid="game-status"]', { timeout: 60000 })
      .should('contain', 'Game Over');

    // Verify winner is displayed
    cy.get('[data-testid="winner-display"]')
      .should('exist')
      .and('contain', 'Winner');

    // Check final scores are displayed
    cy.get('[data-testid="player-score"]')
      .should('have.length', 3);
  });

  after(() => {
    // Cleanup: Logout all users
    Object.values(tokens).forEach((token) => {
      cy.request({
        method: 'POST',
        url: `${Cypress.env('API_URL')}/auth/logout`,
        headers: { Authorization: `Bearer ${token}` }
      });
    });
  });
});
