import json
from unittest.mock import patch, MagicMock
from django.test import TestCase

from backend.tests.fixtures import MockNeo4jTestCase
from backend.game.api.notifications import GameNotifications


class GameNotificationsTestCase(MockNeo4jTestCase):
    """Test case for game notifications"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Mock the channel layer
        self.channel_layer_patcher = patch('backend.game.api.notifications.get_channel_layer')
        self.mock_channel_layer = self.channel_layer_patcher.start()

        # Mock async_to_sync
        self.async_to_sync_patcher = patch('backend.game.api.notifications.async_to_sync')
        self.mock_async_to_sync = self.async_to_sync_patcher.start()

        # Create a mock for the wrapped function
        self.mock_wrapped_func = MagicMock()
        self.mock_async_to_sync.return_value = self.mock_wrapped_func

        # Create a mock channel layer
        self.mock_channel = MagicMock()
        self.mock_channel.group_send = MagicMock()
        self.mock_channel_layer.return_value = self.mock_channel

        # Set up test data
        self.game_id = "game1"
        self.player_id = "player1"
        self.card = {"suit": "hearts", "rank": "A", "value": 14}

    def tearDown(self):
        """Clean up after tests"""
        self.channel_layer_patcher.stop()
        self.async_to_sync_patcher.stop()
        super().tearDown()

    def test_notify_card_played(self):
        """Test notifying that a card was played"""
        # Call the notification method
        result = GameNotifications.notify_card_played(
            game_id=self.game_id,
            player_id=self.player_id,
            card=self.card
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "card_played")
        self.assertEqual(args[1]["data"]["player_id"], self.player_id)
        self.assertEqual(args[1]["data"]["card"], self.card)

    def test_notify_card_drawn(self):
        """Test notifying that a card was drawn"""
        # Call the notification method
        result = GameNotifications.notify_card_drawn(
            game_id=self.game_id,
            player_id=self.player_id
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "card_drawn")
        self.assertEqual(args[1]["data"]["player_id"], self.player_id)

    def test_notify_one_card_announced(self):
        """Test notifying that one card was announced"""
        # Call the notification method
        result = GameNotifications.notify_one_card_announced(
            game_id=self.game_id,
            player_id=self.player_id
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "one_card_announced")
        self.assertEqual(args[1]["data"]["player_id"], self.player_id)

    def test_notify_turn_changed(self):
        """Test notifying that the turn changed"""
        # Call the notification method
        result = GameNotifications.notify_turn_changed(
            game_id=self.game_id,
            player_id=self.player_id
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "turn_changed")
        self.assertEqual(args[1]["data"]["player_id"], self.player_id)

    def test_notify_game_started(self):
        """Test notifying that the game started"""
        # Call the notification method
        result = GameNotifications.notify_game_started(
            game_id=self.game_id
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "game_started")

    def test_notify_game_ended(self):
        """Test notifying that the game ended"""
        # Call the notification method
        result = GameNotifications.notify_game_ended(
            game_id=self.game_id,
            winner_id=self.player_id,
            scores={"player1": 0, "player2": 10}
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "game_ended")
        self.assertEqual(args[1]["data"]["winner_id"], self.player_id)
        self.assertEqual(args[1]["data"]["scores"], {"player1": 0, "player2": 10})

    def test_notify_player_joined(self):
        """Test notifying that a player joined"""
        # Call the notification method
        result = GameNotifications.notify_player_joined(
            game_id=self.game_id,
            player_id=self.player_id,
            player_name="Test Player"
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "player_joined")
        self.assertEqual(args[1]["data"]["player_id"], self.player_id)
        self.assertEqual(args[1]["data"]["player_name"], "Test Player")

    def test_notify_player_left(self):
        """Test notifying that a player left"""
        # Call the notification method
        result = GameNotifications.notify_player_left(
            game_id=self.game_id,
            player_id=self.player_id,
            player_name="Test Player"
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "player_left")
        self.assertEqual(args[1]["data"]["player_id"], self.player_id)
        self.assertEqual(args[1]["data"]["player_name"], "Test Player")

    def test_send_to_player(self):
        """Test sending a notification to a player"""
        # Call the notification method
        result = GameNotifications.send_to_player(
            player_id=self.player_id,
            event_type="test_event",
            data={"test": "data"}
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"player_{self.player_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "test_event")
        self.assertEqual(args[1]["data"], {"test": "data"})

    def test_send_to_game_with_exclude(self):
        """Test sending a notification to a game with excluded player"""
        # Call the notification method
        result = GameNotifications.send_to_game(
            game_id=self.game_id,
            event_type="test_event",
            data={"test": "data"},
            exclude_player_id=self.player_id
        )

        # Check the result
        self.assertTrue(result)

        # Check that async_to_sync was called with channel_layer.group_send
        self.mock_async_to_sync.assert_called_once_with(self.mock_channel.group_send)

        # Check that the wrapped function was called with the right arguments
        self.mock_wrapped_func.assert_called_once()
        args, kwargs = self.mock_wrapped_func.call_args
        self.assertEqual(args[0], f"game_{self.game_id}")
        self.assertEqual(args[1]["type"], "game.notification")
        self.assertEqual(args[1]["event_type"], "test_event")
        self.assertEqual(args[1]["data"], {"test": "data"})
        self.assertEqual(args[1]["exclude_player_id"], self.player_id)

    def test_error_handling(self):
        """Test error handling in notifications"""
        # Make the wrapped function raise an exception
        self.mock_wrapped_func.side_effect = Exception("Test error")

        # Call the notification method
        result = GameNotifications.notify_card_played(
            game_id=self.game_id,
            player_id=self.player_id,
            card=self.card
        )

        # Check the result
        self.assertFalse(result)
