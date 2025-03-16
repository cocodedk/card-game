import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status

from backend.tests.fixtures import MockNeo4jTestCase
from backend.game.models import Game, GameState
from backend.game.models.player import Player
from backend.game.models.game_rule_set import GameRuleSet


class GameAPITestCase(MockNeo4jTestCase):
    """Test case for game API endpoints"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a test user and player
        self.client = Client()
        self.user = MagicMock()
        self.user.id = 1
        self.user.username = "testuser"

        # Create a player
        self.player = MagicMock(spec=Player)
        self.player.uid = "player1"
        self.player.user = self.user
        self.player.username = "testuser"

        # Create another player for testing
        self.player2 = MagicMock(spec=Player)
        self.player2.uid = "player2"
        self.player2.username = "testuser2"

        # Mock the get_object_or_404 function
        self.get_object_or_404_patcher = patch('backend.game.api.views.get_object_or_404')
        self.mock_get_object_or_404 = self.get_object_or_404_patcher.start()
        self.mock_get_object_or_404.side_effect = self.mock_get_object

        # Create a rule set
        self.rule_set = MagicMock(spec=GameRuleSet)
        self.rule_set.uid = "ruleset1"
        self.rule_set.name = "Test Rule Set"
        self.rule_set.parameters = {
            "min_players": 2,
            "max_players": 4
        }

        # Create a game
        self.game = MagicMock(spec=Game)
        self.game.uid = "game1"
        self.game.name = "Test Game"
        self.game.status = "waiting"
        self.game.creator_id = self.player.uid
        self.game.players = [self.player.uid]
        self.game.rule_set.get.return_value = self.rule_set

        # Create a game state
        self.game_state = MagicMock(spec=GameState)
        self.game_state.game = self.game
        self.game_state.current_player_uid = self.player.uid
        self.game_state.next_player_uid = self.player2.uid
        self.game_state.direction = 1
        self.game_state.player_states = {
            self.player.uid: {
                "hand": [{"suit": "hearts", "rank": "A", "value": 1}],
                "score": 0,
                "announced_one_card": False
            }
        }
        self.game_state.discard_pile = [{"suit": "hearts", "rank": "K", "value": 13}]
        self.game_state.draw_pile = [{"suit": "spades", "rank": "Q", "value": 12}]
        self.game_state.serialize.return_value = {
            "game_id": self.game.uid,
            "current_player": self.player.uid,
            "players": [
                {
                    "player_id": self.player.uid,
                    "username": self.player.username,
                    "hand": [{"suit": "hearts", "rank": "A", "value": 1}],
                    "score": 0
                }
            ]
        }

        # Add state attribute to the game mock
        self.game.state = MagicMock()

        # Link game state to game
        self.game.state.all.return_value = [self.game_state]

    def tearDown(self):
        """Clean up after tests"""
        self.get_object_or_404_patcher.stop()
        super().tearDown()

    def mock_get_object(self, model, **kwargs):
        """Mock implementation of get_object_or_404"""
        if model == Player:
            if kwargs.get('user') == self.user:
                return self.player
        elif model == Game:
            if kwargs.get('uid') == self.game.uid:
                return self.game

        # If no match, raise a 404
        from django.http import Http404
        raise Http404("Not found")

    @patch('backend.game.services.game_service.GameService.create_game')
    def test_create_game(self, mock_create_game):
        """Test creating a game"""
        # Mock the create_game method
        mock_create_game.return_value = self.game

        # Set up the request
        url = reverse('create_game')
        data = {
            "rule_set_id": self.rule_set.uid,
            "name": "Test Game"
        }

        # Make the request
        with patch('django.contrib.auth.models.AnonymousUser', return_value=self.user):
            response = self.client.post(
                url,
                json.dumps(data),
                content_type='application/json',
                HTTP_AUTHORIZATION='Bearer fake_token'
            )

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['game_id'], self.game.uid)

    def test_get_game_state(self):
        """Test getting the game state"""
        # Set up the request
        url = reverse('get_game_state', args=[self.game.uid])

        # Make the request
        with patch('django.contrib.auth.models.AnonymousUser', return_value=self.user):
            response = self.client.get(
                url,
                HTTP_AUTHORIZATION='Bearer fake_token'
            )

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['game_id'], self.game.uid)
        self.assertEqual(response_data['current_player'], self.player.uid)

    def test_play_card(self):
        """Test playing a card"""
        # Set up the request
        url = reverse('play_card', args=[self.game.uid])
        data = {
            "card": {"suit": "hearts", "rank": "A", "value": 1}
        }

        # Mock the play_card method
        self.game_state.play_card.return_value = {
            "success": True,
            "effects": {"next_player": self.player2.uid}
        }

        # Make the request
        with patch('django.contrib.auth.models.AnonymousUser', return_value=self.user):
            response = self.client.post(
                url,
                json.dumps(data),
                content_type='application/json',
                HTTP_AUTHORIZATION='Bearer fake_token'
            )

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['effects']['next_player'], self.player2.uid)

    def test_draw_card(self):
        """Test drawing a card"""
        # Set up the request
        url = reverse('draw_card', args=[self.game.uid])

        # Mock the draw_card method
        self.game_state.draw_card.return_value = {"suit": "spades", "rank": "Q", "value": 12}

        # Make the request
        with patch('django.contrib.auth.models.AnonymousUser', return_value=self.user):
            response = self.client.post(
                url,
                content_type='application/json',
                HTTP_AUTHORIZATION='Bearer fake_token'
            )

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['card']['suit'], "spades")
        self.assertEqual(response_data['card']['rank'], "Q")

    def test_announce_one_card(self):
        """Test announcing one card"""
        # Set up the request
        url = reverse('announce_one_card', args=[self.game.uid])

        # Update player hand to have exactly one card
        self.game_state.player_states[self.player.uid]["hand"] = [
            {"suit": "hearts", "rank": "A", "value": 1}
        ]

        # Make the request
        with patch('django.contrib.auth.models.AnonymousUser', return_value=self.user):
            response = self.client.post(
                url,
                content_type='application/json',
                HTTP_AUTHORIZATION='Bearer fake_token'
            )

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], "One card announced successfully")
