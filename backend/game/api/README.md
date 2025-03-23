# Idiot Card Game API Documentation

This document provides information about the API endpoints for the Idiot Card Game.

## Authentication

All API endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

## Game Management Endpoints

### Create a Game

Create a new game with the specified rule set.

- **URL**: `/api/games/create/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "rule_set_id": "string",
    "name": "string"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "game_id": "string",
    "message": "Game created successfully"
  }
  ```

### Join a Game

Join an existing game.

- **URL**: `/api/games/{game_id}/join/`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "success": true,
    "message": "Joined game successfully"
  }
  ```

### Start a Game

Start a game that is in the waiting state. Only the creator can start the game.

- **URL**: `/api/games/{game_id}/start/`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "success": true,
    "message": "Game started successfully",
    "game_state": { ... }
  }
  ```

### List Game Rule Sets

Get a list of all available game rule sets.

- **URL**: `/api/game-rules/`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "rule_sets": [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "version": "string"
      }
    ]
  }
  ```

### Create Rule Set

Create a custom rule set for games.

- **URL**: `/api/game-rules/create/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "name": "string",
    "description": "string",
    "card_actions": {
      // Card action mappings
    },
    "targeting_rules": {
      // Rules for targeting players
    },
    "turn_flow": {
      // Rules for turn progression
    },
    "win_conditions": [
      // Conditions that determine a winner
    ],
    "deck_configuration": {
      // Optional configuration for the deck
    }
  }
  ```
- **Response**:
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "version": "string"
  }
  ```

## Game State Endpoint

### Get Game State

Get the current state of the game.

- **URL**: `/api/games/{game_id}/state/`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "game_id": "string",
    "game_name": "string",
    "status": "string",
    "current_player": "string",
    "next_player": "string",
    "direction": 1,
    "players": [
      {
        "player_id": "string",
        "username": "string",
        "hand": [
          {
            "suit": "string",
            "rank": "string",
            "value": 0
          }
        ],
        "hand_count": 0,
        "score": 0,
        "announced_one_card": false,
        "is_current_player": false,
        "is_next_player": false
      }
    ],
    "discard_pile": [
      {
        "suit": "string",
        "rank": "string",
        "value": 0
      }
    ],
    "top_card": {
      "suit": "string",
      "rank": "string",
      "value": 0
    },
    "draw_pile_count": 0,
    "current_suit": "string",
    "skipped_players": ["string"]
  }
  ```

## Game Action Endpoints

### Play a Card

Play a card from the player's hand.

- **URL**: `/api/games/{game_id}/play-card/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "card": {
      "suit": "string",
      "rank": "string",
      "value": 0
    },
    "target_player_id": "string",  // Optional, required for certain cards
    "chosen_suit": "string"        // Optional, required for Jack
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "effects": {
      "next_player": "string",
      "direction_changed": false,
      "cards_drawn": 0,
      "skipped": false
    },
    "game_state": { ... }
  }
  ```

### Draw a Card

Draw a card from the draw pile.

- **URL**: `/api/games/{game_id}/draw-card/`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "success": true,
    "card": {
      "suit": "string",
      "rank": "string",
      "value": 0
    },
    "game_state": { ... }
  }
  ```

### Announce One Card

Announce that the player has only one card left.

- **URL**: `/api/games/{game_id}/announce-one-card/`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "success": true,
    "message": "One card announced successfully"
  }
  ```

## Error Responses

All endpoints may return the following error responses:

- **401 Unauthorized**: Authentication token is missing or invalid
- **403 Forbidden**: The authenticated user does not have permission to perform the action
- **404 Not Found**: The requested resource was not found
- **400 Bad Request**: The request was invalid or cannot be processed

Example error response:
```json
{
  "error": "Error message describing the issue"
}
```
