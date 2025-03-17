declare namespace Cypress {
  interface Chainable {
    login(username: string, password: string): Chainable<void>;
    createGame(config: GameConfig): Chainable<string>;
    joinGame(gameId: string): Chainable<void>;
    playCard(cardIndex: number): Chainable<void>;
    drawCard(): Chainable<void>;
    passTurn(): Chainable<void>;
  }
}

interface GameConfig {
  game_type: string;
  max_players: number;
  time_limit: number;
  use_ai: boolean;
}

// Login command
Cypress.Commands.add('login', (username: string, password: string) => {
  cy.get('[data-testid="login-username"]').type(username);
  cy.get('[data-testid="login-password"]').type(password);
  cy.get('[data-testid="login-submit"]').click();
});

// Create game command
Cypress.Commands.add('createGame', (config: GameConfig) => {
  cy.get('[data-testid="create-game-button"]').click();
  cy.get('[data-testid="game-type-select"]').select(config.game_type);
  cy.get('[data-testid="max-players-input"]').type(config.max_players.toString());
  cy.get('[data-testid="time-limit-input"]').type(config.time_limit.toString());
  cy.get('[data-testid="create-game-submit"]').click();

  return cy.url().then((url) => url.split('/').pop() || '');
});

// Join game command
Cypress.Commands.add('joinGame', (gameId: string) => {
  cy.visit(`/game/${gameId}`);
  cy.get('[data-testid="join-game-button"]').click();
  cy.get('[data-testid="player-ready-button"]').click();
});

// Play card command
Cypress.Commands.add('playCard', (cardIndex: number) => {
  cy.get('[data-testid="card"]').eq(cardIndex).click();
});

// Draw card command
Cypress.Commands.add('drawCard', () => {
  cy.get('[data-testid="draw-card-button"]').click();
});

// Pass turn command
Cypress.Commands.add('passTurn', () => {
  cy.get('[data-testid="pass-turn-button"]').click();
});
