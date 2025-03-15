"""
Notification system for real-time game events.
This module provides functionality to send real-time notifications to players
about game events using Django Channels.
"""

import json
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class GameNotifications:
    """
    Handles sending real-time notifications for game events.
    Uses Django Channels to send WebSocket messages to connected clients.
    """

    @staticmethod
    def get_player_group_name(player_id):
        """
        Get the channel group name for a player.

        Args:
            player_id: The ID of the player

        Returns:
            str: The channel group name
        """
        return f"player_{player_id}"

    @staticmethod
    def get_game_group_name(game_id):
        """
        Get the channel group name for a game.

        Args:
            game_id: The ID of the game

        Returns:
            str: The channel group name
        """
        return f"game_{game_id}"

    @classmethod
    def send_to_player(cls, player_id, event_type, data):
        """
        Send a notification to a specific player.

        Args:
            player_id: The ID of the player
            event_type: The type of event
            data: The data to send

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        try:
            channel_layer = get_channel_layer()
            group_name = cls.get_player_group_name(player_id)

            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "game.notification",
                    "event_type": event_type,
                    "data": data
                }
            )
            return True
        except Exception as e:
            logger.error(f"Error sending notification to player {player_id}: {str(e)}")
            return False

    @classmethod
    def send_to_game(cls, game_id, event_type, data, exclude_player_id=None):
        """
        Send a notification to all players in a game.

        Args:
            game_id: The ID of the game
            event_type: The type of event
            data: The data to send
            exclude_player_id: Optional player ID to exclude from the notification

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        try:
            channel_layer = get_channel_layer()
            group_name = cls.get_game_group_name(game_id)

            message = {
                "type": "game.notification",
                "event_type": event_type,
                "data": data
            }

            if exclude_player_id:
                message["exclude_player_id"] = exclude_player_id

            async_to_sync(channel_layer.group_send)(
                group_name,
                message
            )
            return True
        except Exception as e:
            logger.error(f"Error sending notification to game {game_id}: {str(e)}")
            return False

    # Specific event notifications

    @classmethod
    def notify_card_played(cls, game_id, player_id, card, effects=None):
        """
        Notify all players that a card was played.

        Args:
            game_id: The ID of the game
            player_id: The ID of the player who played the card
            card: The card that was played
            effects: Optional effects of the card play

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "player_id": player_id,
            "card": card
        }

        if effects:
            data["effects"] = effects

        return cls.send_to_game(game_id, "card_played", data)

    @classmethod
    def notify_card_drawn(cls, game_id, player_id):
        """
        Notify all players that a player drew a card.

        Args:
            game_id: The ID of the game
            player_id: The ID of the player who drew a card

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "player_id": player_id
        }

        return cls.send_to_game(game_id, "card_drawn", data)

    @classmethod
    def notify_one_card_announced(cls, game_id, player_id):
        """
        Notify all players that a player announced one card.

        Args:
            game_id: The ID of the game
            player_id: The ID of the player who announced one card

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "player_id": player_id
        }

        return cls.send_to_game(game_id, "one_card_announced", data)

    @classmethod
    def notify_turn_changed(cls, game_id, player_id):
        """
        Notify all players that the turn has changed.

        Args:
            game_id: The ID of the game
            player_id: The ID of the player whose turn it is now

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "player_id": player_id
        }

        return cls.send_to_game(game_id, "turn_changed", data)

    @classmethod
    def notify_game_started(cls, game_id):
        """
        Notify all players that the game has started.

        Args:
            game_id: The ID of the game

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        return cls.send_to_game(game_id, "game_started", {})

    @classmethod
    def notify_game_ended(cls, game_id, winner_id, scores):
        """
        Notify all players that the game has ended.

        Args:
            game_id: The ID of the game
            winner_id: The ID of the winner
            scores: The final scores

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "winner_id": winner_id,
            "scores": scores
        }

        return cls.send_to_game(game_id, "game_ended", data)

    @classmethod
    def notify_player_joined(cls, game_id, player_id, player_name):
        """
        Notify all players that a new player has joined the game.

        Args:
            game_id: The ID of the game
            player_id: The ID of the player who joined
            player_name: The name of the player who joined

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "player_id": player_id,
            "player_name": player_name
        }

        return cls.send_to_game(game_id, "player_joined", data)

    @classmethod
    def notify_player_left(cls, game_id, player_id, player_name):
        """
        Notify all players that a player has left the game.

        Args:
            game_id: The ID of the game
            player_id: The ID of the player who left
            player_name: The name of the player who left

        Returns:
            bool: True if the notification was sent, False otherwise
        """
        data = {
            "player_id": player_id,
            "player_name": player_name
        }

        return cls.send_to_game(game_id, "player_left", data)
