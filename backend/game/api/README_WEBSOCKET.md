# Idiot Card Game WebSocket API Documentation

This document provides information about the WebSocket API for real-time game events in the Idiot Card Game.

## Connection

Connect to the WebSocket server using the following URL:

```
ws://<server>/ws/games/<game_id>/
```

### Authentication

Authentication is required for WebSocket connections. You can authenticate in two ways:

1. **Query Parameter**: Add a `token` query parameter with your JWT token:
   ```
   ws://<server>/ws/games/<game_id>/?token=<jwt_token>
   ```

2. **Authorization Header**: Include an Authorization header with your JWT token:
   ```
   Authorization: Bearer <jwt_token>
   ```

### Connection Events

When you successfully connect to the WebSocket server, you will receive a connection confirmation:

```json
{
  "type": "connection_established",
  "game_id": "string",
  "player_id": "string"
}
```

## Game Events

The WebSocket connection will receive real-time events for the game. Each event has a `type` field that indicates the type of event, and a `data` field that contains the event data.

### Card Played

Sent when a player plays a card.

```json
{
  "type": "card_played",
  "data": {
    "player_id": "string",
    "card": {
      "suit": "string",
      "rank": "string",
      "value": 0
    },
    "effects": {
      "next_player": "string",
      "direction_changed": false,
      "cards_drawn": 0,
      "skipped": false
    }
  }
}
```

### Card Drawn

Sent when a player draws a card.

```json
{
  "type": "card_drawn",
  "data": {
    "player_id": "string"
  }
}
```

### One Card Announced

Sent when a player announces they have one card left.

```json
{
  "type": "one_card_announced",
  "data": {
    "player_id": "string"
  }
}
```

### Turn Changed

Sent when the turn changes to a different player.

```json
{
  "type": "turn_changed",
  "data": {
    "player_id": "string"
  }
}
```

### Game Started

Sent when the game starts.

```json
{
  "type": "game_started",
  "data": {}
}
```

### Game Ended

Sent when the game ends.

```json
{
  "type": "game_ended",
  "data": {
    "winner_id": "string",
    "scores": {
      "player_id": 0
    }
  }
}
```

### Player Joined

Sent when a player joins the game.

```json
{
  "type": "player_joined",
  "data": {
    "player_id": "string",
    "player_name": "string"
  }
}
```

### Player Left

Sent when a player leaves the game.

```json
{
  "type": "player_left",
  "data": {
    "player_id": "string",
    "player_name": "string"
  }
}
```

## Client Messages

You can send messages to the WebSocket server. Each message should be a JSON object with a `type` field that indicates the type of message.

### Ping

Send a ping message to check if the connection is alive.

```json
{
  "type": "ping"
}
```

The server will respond with a pong message:

```json
{
  "type": "pong"
}
```

## Testing

You can use the provided WebSocket client for testing:

```bash
python -m backend.tests.test_websocket_client ws://<server>/ws/games/<game_id>/ --token=<jwt_token>
```

This client will connect to the WebSocket server and listen for messages. It will also send a ping message to check if the connection is alive.
