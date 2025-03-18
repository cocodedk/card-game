/// <reference types="cypress" />
import { v4 as uuidv4 } from 'uuid';

interface TestUser {
  username: string;
  email: string;
  password: string;
  confirm_password: string;
}

describe('Complete Game Flow', () => {
  // Test users for our game
  const users: TestUser[] = [
    { username: 'player1', email: 'player1@test.com', password: 'testpass1', confirm_password: 'testpass1' },
    { username: 'player2', email: 'player2@test.com', password: 'testpass2', confirm_password: 'testpass2' },
    { username: 'player3', email: 'player3@test.com', password: 'testpass3', confirm_password: 'testpass3' },
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

  beforeEach(() => {
    // Increase the timeout for each test
    Cypress.config('defaultCommandTimeout', 10000);

    // Log all API requests
    cy.intercept('**/*').as('allRequests');

    // Specific API endpoints we want to monitor
    cy.intercept('POST', '**/auth/login').as('login');
    cy.intercept('POST', '**/auth/register').as('register');
    cy.intercept('POST', '**/games/create').as('createGame');
    cy.intercept('POST', '**/games/*/join').as('joinGame');
    cy.intercept('POST', '**/games/*/ready').as('readyGame');
    cy.intercept('POST', '**/games/*/start').as('startGame');
    cy.intercept('GET', '**/games/*').as('getGame');
    cy.intercept('WS', '**/ws/**').as('websocket');

    // Log network activity
    cy.on('log:added', (log) => {
      if (log.displayName === 'xhr' || log.displayName === 'request') {
        cy.log(`📡 ${log.displayName.toUpperCase()}: ${log.url}`);
        if (log.response) {
          cy.log(`📥 Response: ${JSON.stringify(log.response.body, null, 2)}`);
        }
      }
    });

    // Handle uncaught exceptions
    Cypress.on('uncaught:exception', (err: Error, runnable: Mocha.Runnable) => {
      console.log('Uncaught exception:', err);
      return false;
    });
  });

  before(() => {
    cy.log('=== Starting User Setup ===');

    // Sequential user registration and login
    const setupUsers = () => {
      const setupUser = (index: number) => {
        if (index >= users.length) {
          cy.log('=== All Users Setup Complete ===');
          return;
        }

        const user = users[index];
        cy.log(`Setting up user: ${user.username}`);

        // Try to register
        cy.request({
          method: 'POST',
          url: `${Cypress.env('API_URL')}/auth/register`,
          body: {
            username: user.username,
            email: user.email,
            password: user.password,
            confirm_password: user.password,
            first_name: "",
            last_name: ""
          },
          failOnStatusCode: false
        }).then((registerResponse) => {
          if (registerResponse.status === 201) {
            cy.log(`✓ ${user.username} registered successfully`);
          } else if (registerResponse.status === 400) {
            cy.log(`ℹ ${user.username} already exists, proceeding to login`);
          } else {
            cy.log(`⚠ Unexpected registration response for ${user.username}: ${registerResponse.status}`);
          }

          // Login regardless of registration result
          cy.request({
            method: 'POST',
            url: `${Cypress.env('API_URL')}/auth/login`,
            body: {
              username: user.username,
              password: user.password
            },
            failOnStatusCode: true
          }).then((loginResponse) => {
            expect(loginResponse.status).to.equal(200);
            expect(loginResponse.body.tokens).to.have.property('access');
            expect(loginResponse.body.user.username).to.equal(user.username);

            tokens[user.username] = loginResponse.body.tokens.access;
            cy.log(`✓ ${user.username} logged in successfully`);
            cy.log(`✓ Token stored for ${user.username}`);

            // Process next user
            setupUser(index + 1);
          });
        });
      };

      // Start with first user
      setupUser(0);
    };

    // Start user setup process
    setupUsers();

    // Verify all users are set up before proceeding
    cy.wrap(null).then(() => {
      cy.log('=== Verifying User Setup ===');
      let allUsersReady = true;

      users.forEach((user) => {
        if (!tokens[user.username]) {
          allUsersReady = false;
          cy.log(`⚠ Missing token for ${user.username}`);
        } else {
          cy.log(`✓ Verified token for ${user.username}`);
        }
      });

      expect(allUsersReady, 'All users should be set up with tokens').to.be.true;
      cy.log('=== User Setup Verification Complete ===');
    });
  });

  it('Player1 creates a game', () => {
    cy.log('=== Creating New Game ===');

    // Login as Player1
    cy.visit('/', { timeout: 10000 });
    cy.get('[data-testid="login-username"]', { timeout: 10000 }).type(users[0].username);
    cy.get('[data-testid="login-password"]').type(users[0].password);
    cy.get('[data-testid="login-submit"]').click();

    // Wait for login response
    cy.wait('@login').then((interception) => {
      cy.log(`📥 Login Response: ${JSON.stringify(interception.response?.body, null, 2)}`);
    });

    // Create game with network monitoring
    cy.log('Creating game with config:', gameConfig);
    cy.get('[data-testid="create-game-button"]', { timeout: 10000 }).click();
    cy.get('[data-testid="game-type-select"]').select(gameConfig.game_type);
    cy.get('[data-testid="max-players-input"]').clear().type(gameConfig.max_players.toString());
    cy.get('[data-testid="time-limit-input"]').clear().type(gameConfig.time_limit.toString());
    cy.get('[data-testid="create-game-submit"]').click();

    // Wait for game creation response
    cy.wait('@createGame').then((interception) => {
      cy.log(`📥 Game Creation Response: ${JSON.stringify(interception.response?.body, null, 2)}`);
    });

    // Wait for redirect and store game ID
    cy.url().should('include', '/game/').then((url) => {
      gameId = url.split('/').pop() || '';
      expect(gameId).to.not.be.empty;
      cy.log(`✓ Game created with ID: ${gameId}`);
    });

    // Wait for game creation confirmation
    cy.get('[data-testid="game-status"]', { timeout: 10000 })
      .should('be.visible')
      .should('contain', 'Waiting for players');

    cy.log('=== Game Creation Complete ===');
  });

  it('Other players join the game', () => {
    cy.log('=== Players Joining Game ===');
    expect(gameId, 'Game ID should be defined').to.not.be.undefined;
    cy.log(`Joining game with ID: ${gameId}`);

    // Player 2 joins with network monitoring
    cy.log('Player 2 joining...');
    cy.visit(`/game/${gameId}`);
    cy.get('[data-testid="login-username"]').type(users[1].username);
    cy.get('[data-testid="login-password"]').type(users[1].password);
    cy.get('[data-testid="login-submit"]').click();

    cy.wait('@login').then((interception) => {
      cy.log(`📥 Player 2 Login Response: ${JSON.stringify(interception.response?.body, null, 2)}`);
    });

    cy.get('[data-testid="join-game-button"]').should('be.visible').click();
    cy.wait('@joinGame').then((interception) => {
      cy.log(`📥 Player 2 Join Response: ${JSON.stringify(interception.response?.body, null, 2)}`);
    });

    cy.get('[data-testid="player-ready-button"]').should('be.visible').click();
    cy.log('✓ Player 2 joined and ready');

    // Player 3 joins
    cy.log('Player 3 joining...');
    cy.visit(`/game/${gameId}`);
    cy.get('[data-testid="login-username"]').type(users[2].username);
    cy.get('[data-testid="login-password"]').type(users[2].password);
    cy.get('[data-testid="login-submit"]').click();
    cy.get('[data-testid="join-game-button"]').should('be.visible').click();
    cy.get('[data-testid="player-ready-button"]').should('be.visible').click();
    cy.log('✓ Player 3 joined and ready');

    // Back to Player 1 to start the game
    cy.log('Player 1 preparing to start game...');
    cy.visit(`/game/${gameId}`);
    cy.get('[data-testid="login-username"]').type(users[0].username);
    cy.get('[data-testid="login-password"]').type(users[0].password);
    cy.get('[data-testid="login-submit"]').click();
    cy.get('[data-testid="player-ready-button"]').should('be.visible').click();

    // Verify all players are ready
    cy.get('[data-testid="player-status"]', { timeout: 10000 })
      .should('have.length', 3)
      .each(($el) => {
        cy.wrap($el).should('contain', 'Ready');
      });
    cy.log('✓ All players ready');

    // Start game
    cy.get('[data-testid="start-game-button"]').should('be.visible').click();
    cy.get('[data-testid="game-status"]').should('contain', 'Game in progress');
    cy.log('✓ Game started successfully');

    cy.log('=== Game Join Phase Complete ===');
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
