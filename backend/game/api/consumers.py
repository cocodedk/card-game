"""
WebSocket consumers for real-time game events.
This module provides WebSocket consumers for handling real-time game events.
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from backend.game.models.player import Player

logger = logging.getLogger(__name__)


class GameConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for game events.
    Handles real-time communication for game events.
    """

    async def connect(self):
        """
        Handle WebSocket connection.
        Authenticate the user and add them to the appropriate groups.
        """
        # Get the game ID from the URL route
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f"game_{self.game_id}"

        # Authenticate the user
        user = self.scope.get('user', AnonymousUser())
        token = self.scope.get('token', None)

        if isinstance(user, AnonymousUser) and token:
            try:
                # Validate the token
                access_token = AccessToken(token)
                user_id = access_token.payload.get('user_id')

                if user_id:
                    # Get the player
                    self.player = await self.get_player(user_id)
                    if self.player:
                        self.player_id = self.player.uid
                        self.player_group_name = f"player_{self.player_id}"

                        # Add the player to the game group
                        await self.channel_layer.group_add(
                            self.game_group_name,
                            self.channel_name
                        )

                        # Add the player to their own group
                        await self.channel_layer.group_add(
                            self.player_group_name,
                            self.channel_name
                        )

                        # Accept the connection
                        await self.accept()

                        # Send a connection confirmation
                        await self.send(text_data=json.dumps({
                            'type': 'connection_established',
                            'game_id': self.game_id,
                            'player_id': self.player_id
                        }))
                        return
            except TokenError:
                pass

        # If authentication failed, close the connection
        await self.close()

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnection.
        Remove the user from the appropriate groups.

        Args:
            close_code: The close code
        """
        # Leave the game group
        if hasattr(self, 'game_group_name'):
            await self.channel_layer.group_discard(
                self.game_group_name,
                self.channel_name
            )

        # Leave the player group
        if hasattr(self, 'player_group_name'):
            await self.channel_layer.group_discard(
                self.player_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.

        Args:
            text_data: The message data
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            # Handle different message types
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
            else:
                logger.warning(f"Received unknown message type: {message_type}")
        except json.JSONDecodeError:
            logger.error("Received invalid JSON data")

    async def game_notification(self, event):
        """
        Handle game notification events.

        Args:
            event: The event data
        """
        # Check if this notification should exclude this player
        exclude_player_id = event.get('exclude_player_id')
        if exclude_player_id and hasattr(self, 'player_id') and exclude_player_id == self.player_id:
            return

        # Forward the notification to the WebSocket
        await self.send(text_data=json.dumps({
            'type': event.get('event_type'),
            'data': event.get('data', {})
        }))

    @database_sync_to_async
    def get_player(self, user_id):
        """
        Get a player by user ID.

        Args:
            user_id: The user ID

        Returns:
            Player: The player object or None
        """
        try:
            return Player.nodes.get(user_id=user_id)
        except Player.DoesNotExist:
            return None
