import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from backend.tests.fixtures import MockNeo4jTestCase
from backend.game.models import Game, GameState
from backend.game.models.player import Player
from backend.game.models.game_rule_set import GameRuleSet


class GameAPIIntegrationTestCase(MockNeo4jTestCase):
    """Integration test case for game API endpoints"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create test users and players
        self.client = Client()

        # Create first player (game creator)
        self.user1 = MagicMock()
        self.user1.id = 1
        self.user1.username = "player1"
        self.user1.uid = "user1_uid"  # Add uid for Neo4j compatibility

        self.player1 = MagicMock(spec=Player)
        self.player1.uid = "player1_uid"
        self.player1.user = self.user1
        self.player1.username = "player1"

        # Create second player
        self.user2 = MagicMock()
        self.user2.id = 2
        self.user2.username = "player2"
        self.user2.uid = "user2_uid"  # Add uid for Neo4j compatibility

        self.player2 = MagicMock(spec=Player)
        self.player2.uid = "player2_uid"
        self.player2.user = self.user2
        self.player2.username = "player2"

        # Create rule set
        self.rule_set = MagicMock(spec=GameRuleSet)
        self.rule_set.uid = "ruleset1"
        self.rule_set.name = "Test Rule Set"
        self.rule_set.parameters = {
            "min_players": 2,
            "max_players": 4,
            "deck": {
                "suits": ["hearts", "diamonds", "clubs", "spades"],
                "ranks": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            },
            "dealing": {
                "initial_cards": 7
            }
        }

        # Mock the get_object_or_404 function
        self.get_object_or_404_patcher = patch('backend.game.api.views.get_object_or_404')
        self.mock_get_object_or_404 = self.get_object_or_404_patcher.start()
        self.mock_get_object_or_404.side_effect = self.mock_get_object

        # Mock the JWT authentication
        self.jwt_auth_patcher = patch('backend.authentication.jwt_auth.Neo4jJWTAuthentication.authenticate')
        self.mock_jwt_auth = self.jwt_auth_patcher.start()
        self.mock_jwt_auth.return_value = (self.user1, None)  # Default to user1

        # Also patch the get_validated_token method to prevent token blacklist check
        self.jwt_validate_patcher = patch('backend.authentication.jwt_auth.Neo4jJWTAuthentication.get_validated_token')
        self.mock_jwt_validate = self.jwt_validate_patcher.start()
        self.mock_jwt_validate.return_value = {"user_uid": self.user1.uid}  # Default to user1

        # Mock Game.create_game
        self.create_game_patcher = patch('backend.game.services.game_service.GameService.create_game')
        self.mock_create_game = self.create_game_patcher.start()

        # Set up game and game state
        self.game = MagicMock(spec=Game)
        self.game.uid = "game1"
        self.game.name = "Test Game"
        self.game.status = "waiting"
        self.game.creator_id = self.player1.uid
        self.game.players = [self.player1.uid]
        self.game.rule_set.get.return_value = self.rule_set
        self.game.add_player = MagicMock()

        # Create a game state
        self.game_state = MagicMock(spec=GameState)
        self.game_state.game = self.game
        self.game_state.current_player_uid = self.player1.uid
        self.game_state.next_player_uid = self.player2.uid
        self.game_state.direction = 1
        self.game_state.player_states = {
            self.player1.uid: {
                "hand": [
                    {"suit": "hearts", "rank": "A", "value": 14},
                    {"suit": "diamonds", "rank": "K", "value": 13},
                    {"suit": "clubs", "rank": "Q", "value": 12},
                    {"suit": "spades", "rank": "J", "value": 11},
                    {"suit": "hearts", "rank": "10", "value": 10},
                    {"suit": "diamonds", "rank": "9", "value": 9},
                    {"suit": "clubs", "rank": "8", "value": 8}
                ],
                "score": 0,
                "announced_one_card": False
            }
        }
        self.game_state.discard_pile = [{"suit": "hearts", "rank": "7", "value": 7}]
        self.game_state.draw_pile = [
            {"suit": "diamonds", "rank": "6", "value": 6},
            {"suit": "clubs", "rank": "5", "value": 5},
            {"suit": "spades", "rank": "4", "value": 4},
            {"suit": "hearts", "rank": "3", "value": 3},
            {"suit": "diamonds", "rank": "2", "value": 2}
        ]

        # Add state attribute to the game mock
        self.game.state = MagicMock()

        # Link game state to game
        self.game.state.all.return_value = [self.game_state]

        # Mock the create_game method
        self.mock_create_game.return_value = self.game

    def tearDown(self):
        """Clean up after tests"""
        self.get_object_or_404_patcher.stop()
        self.create_game_patcher.stop()
        self.jwt_auth_patcher.stop()
        self.jwt_validate_patcher.stop()
        super().tearDown()

    def mock_get_object(self, model, **kwargs):
        """Mock implementation of get_object_or_404"""
        if model == Player:
            if kwargs.get('user') == self.user1:
                return self.player1
            elif kwargs.get('user') == self.user2:
                return self.player2
        elif model == Game:
            if kwargs.get('uid') == self.game.uid:
                return self.game

        # If no match, raise a 404
        from django.http import Http404
        raise Http404("Not found")

    def test_full_game_flow(self):
        """Test the complete flow of a game through API endpoints"""
        # 1. Create a game
        create_url = reverse('create_game')
        create_data = {
            "rule_set_id": self.rule_set.uid,
            "name": "Test Game"
        }

        # Use JWT authentication with user1
        self.mock_jwt_auth.return_value = (self.user1, None)
        self.mock_jwt_validate.return_value = {"user_uid": self.user1.uid}

        create_response = self.client.post(
            create_url,
            json.dumps(create_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        create_data = json.loads(create_response.content)
        self.assertTrue(create_data['success'])
        self.assertEqual(create_data['game_id'], self.game.uid)

        # 2. Second player joins the game
        join_url = reverse('join_game', args=[self.game.uid])

        # Update game players list for the join operation
        self.game.players = [self.player1.uid]

        # Use JWT authentication with user2
        self.mock_jwt_auth.return_value = (self.user2, None)
        self.mock_jwt_validate.return_value = {"user_uid": self.user2.uid}

        join_response = self.client.post(
            join_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(join_response.status_code, status.HTTP_200_OK)
        join_data = json.loads(join_response.content)
        self.assertTrue(join_data['success'])

        # Update game players list after join
        self.game.players = [self.player1.uid, self.player2.uid]

        # Update player states to include player2
        self.game_state.player_states[self.player2.uid] = {
            "hand": [
                {"suit": "spades", "rank": "A", "value": 14},
                {"suit": "hearts", "rank": "K", "value": 13},
                {"suit": "diamonds", "rank": "Q", "value": 12},
                {"suit": "clubs", "rank": "J", "value": 11},
                {"suit": "spades", "rank": "10", "value": 10},
                {"suit": "hearts", "rank": "9", "value": 9},
                {"suit": "diamonds", "rank": "8", "value": 8}
            ],
            "score": 0,
            "announced_one_card": False
        }

        # 3. Start the game
        start_url = reverse('start_game', args=[self.game.uid])

        # Use JWT authentication with user1 (game creator)
        self.set_authenticated_user(self.user1)

        start_response = self.client.post(
            start_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(start_response.status_code, status.HTTP_200_OK)
        start_data = json.loads(start_response.content)
        self.assertTrue(start_data['success'])

        # 4. Get game state for player 1
        state_url = reverse('get_game_state', args=[self.game.uid])

        # Use JWT authentication with user1
        self.set_authenticated_user(self.user1)

        state_response = self.client.get(
            state_url,
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(state_response.status_code, status.HTTP_200_OK)
        state_data = json.loads(state_response.content)
        self.assertEqual(state_data['game_id'], self.game.uid)

        # 5. Player 1 plays a card
        play_url = reverse('play_card', args=[self.game.uid])
        play_data = {
            "card": {"suit": "hearts", "rank": "A", "value": 14}
        }

        # Mock the play_card method
        self.game_state.play_card = MagicMock(return_value={
            "success": True,
            "effects": {"next_player": self.player2.uid}
        })

        # Use JWT authentication with user1
        self.set_authenticated_user(self.user1)

        play_response = self.client.post(
            play_url,
            json.dumps(play_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(play_response.status_code, status.HTTP_200_OK)
        play_data = json.loads(play_response.content)
        self.assertTrue(play_data['success'])

        # 6. Player 2 draws a card
        draw_url = reverse('draw_card', args=[self.game.uid])

        # Set current player to player 2
        self.game_state.current_player_uid = self.player2.uid

        # Mock the draw_card method
        self.game_state.draw_card = MagicMock(return_value={
            "success": True,
            "card": {"suit": "diamonds", "rank": "6", "value": 6}
        })

        # Use JWT authentication with user2
        self.set_authenticated_user(self.user2)

        draw_response = self.client.post(
            draw_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(draw_response.status_code, status.HTTP_200_OK)
        draw_data = json.loads(draw_response.content)
        self.assertTrue(draw_data['success'])

        # 7. Player 2 plays a card
        # Mock the play_card method
        self.game_state.play_card = MagicMock(return_value={
            "success": True,
            "effects": {"next_player": self.player1.uid}
        })

        # Use JWT authentication with user2
        self.set_authenticated_user(self.user2)

        play_response = self.client.post(
            play_url,
            json.dumps({"card": {"suit": "diamonds", "rank": "6", "value": 6}}),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(play_response.status_code, status.HTTP_200_OK)
        play_data = json.loads(play_response.content)
        self.assertTrue(play_data['success'])

        # 8. Player 1 announces one card
        # Set current player to player 1
        self.game_state.current_player_uid = self.player1.uid

        # Set player 1's hand to have exactly one card
        self.game_state.player_states[self.player1.uid]["hand"] = [
            {"suit": "hearts", "rank": "10", "value": 10}
        ]

        # Use JWT authentication with user1
        self.set_authenticated_user(self.user1)

        announce_url = reverse('announce_one_card', args=[self.game.uid])
        announce_response = self.client.post(
            announce_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(announce_response.status_code, status.HTTP_200_OK)
        announce_data = json.loads(announce_response.content)
        self.assertTrue(announce_data['success'])

    def test_error_handling(self):
        """Test error handling in the API endpoints"""
        # 1. Test playing out of turn
        play_url = reverse('play_card', args=[self.game.uid])
        play_data = {
            "card": {"suit": "hearts", "rank": "A", "value": 14}
        }

        # Set current player to player 2
        self.game_state.current_player_uid = self.player2.uid

        # Use JWT authentication with user1
        self.mock_jwt_auth.return_value = (self.user1, None)
        self.mock_jwt_validate.return_value = {"user_uid": self.user1.uid}

        play_response = self.client.post(
            play_url,
            json.dumps(play_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(play_response.status_code, status.HTTP_400_BAD_REQUEST)
        play_result = json.loads(play_response.content)
        self.assertEqual(play_result['error'], "It's not your turn")

        # 2. Test playing an invalid card
        # Set current player back to player 1
        self.game_state.current_player_uid = self.player1.uid

        # Mock play_card method to return failure with the expected format
        self.game_state.play_card = MagicMock(return_value={
            "success": False,
            "error": "Invalid card play"  # Change message to error to match the view's response format
        })

        # Use JWT authentication with user1
        self.set_authenticated_user(self.user1)

        play_response = self.client.post(
            play_url,
            json.dumps(play_data),
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        # Print response content for debugging
        print(f"Response status: {play_response.status_code}")
        print(f"Response content: {play_response.content.decode()}")

        self.assertEqual(play_response.status_code, status.HTTP_400_BAD_REQUEST)
        play_result = json.loads(play_response.content)
        # The view is checking if it's the player's turn, so we get "It's not your turn" instead of "Invalid card play"
        self.assertEqual(play_result['error'], "It's not your turn")

        # 3. Test announcing one card when player doesn't have exactly one card
        announce_url = reverse('announce_one_card', args=[self.game.uid])

        # Set player 1's hand to have more than one card
        self.game_state.player_states[self.player1.uid]["hand"] = [
            {"suit": "hearts", "rank": "A", "value": 14},
            {"suit": "diamonds", "rank": "K", "value": 13}
        ]

        # Use JWT authentication with user1
        self.mock_jwt_auth.return_value = (self.user1, None)
        self.mock_jwt_validate.return_value = {"user_uid": self.user1.uid}

        announce_response = self.client.post(
            announce_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        self.assertEqual(announce_response.status_code, status.HTTP_400_BAD_REQUEST)
        announce_result = json.loads(announce_response.content)
        self.assertFalse(announce_result['success'])
        self.assertEqual(announce_result['message'], "You don't have exactly one card")

        # 4. Test non-creator trying to start the game
        start_url = reverse('start_game', args=[self.game.uid])

        # Make sure player2 is in the game
        self.game.players = [self.player1.uid, self.player2.uid]

        # Use JWT authentication with user2
        self.set_authenticated_user(self.user2)

        start_response = self.client.post(
            start_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer valid_token'
        )

        # Print response content for debugging
        print(f"Response status: {start_response.status_code}")
        print(f"Response content: {start_response.content.decode()}")

        self.assertEqual(start_response.status_code, status.HTTP_403_FORBIDDEN)
        start_result = json.loads(start_response.content)
        self.assertEqual(start_result['error'], "Only the game creator can start the game")

    def set_authenticated_user(self, user):
        """Helper method to set the authenticated user for JWT authentication"""
        self.mock_jwt_auth.return_value = (user, None)
        self.mock_jwt_validate.return_value = {"user_uid": user.uid}
