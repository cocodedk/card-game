"""
WebSocket client for testing.
This module provides a simple WebSocket client for testing WebSocket connections.
"""

import asyncio
import json
import websockets
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def connect_and_listen(uri, token=None):
    """
    Connect to a WebSocket server and listen for messages.

    Args:
        uri: The WebSocket URI
        token: Optional JWT token for authentication
    """
    # Add token to URI if provided
    if token:
        uri = f"{uri}?token={token}"

    logger.info(f"Connecting to {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")

            # Send a ping message
            await websocket.send(json.dumps({
                "type": "ping"
            }))

            # Listen for messages
            while True:
                message = await websocket.recv()
                logger.info(f"Received message: {message}")

                # Parse the message
                try:
                    data = json.loads(message)
                    message_type = data.get('type')

                    # Handle different message types
                    if message_type == 'pong':
                        logger.info("Received pong response")
                    elif message_type == 'connection_established':
                        logger.info(f"Connection established for game {data.get('game_id')} as player {data.get('player_id')}")
                    else:
                        logger.info(f"Received {message_type} event: {data.get('data', {})}")
                except json.JSONDecodeError:
                    logger.error("Received invalid JSON data")
    except websockets.exceptions.ConnectionClosed as e:
        logger.error(f"Connection closed: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description='WebSocket client for testing')
    parser.add_argument('uri', help='WebSocket URI')
    parser.add_argument('--token', help='JWT token for authentication')

    args = parser.parse_args()

    # Run the client
    asyncio.run(connect_and_listen(args.uri, args.token))


if __name__ == '__main__':
    main()
