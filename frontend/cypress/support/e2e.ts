import './commands';

// Prevent TypeScript errors when accessing the "cy" object
declare global {
  namespace Cypress {
    interface Chainable {
      login(username: string, password: string): void;
      createGame(config: GameConfig): Chainable<string>;
      joinGame(gameId: string): void;
      playCard(cardIndex: number): void;
      drawCard(): void;
      passTurn(): void;
    }
  }
}

interface GameConfig {
  game_type: string;
  max_players: number;
  time_limit: number;
  use_ai: boolean;
}
