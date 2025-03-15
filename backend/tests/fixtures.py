"""
Test fixtures for Django tests.
This module contains fixtures for setting up the test environment.
"""
import os
from unittest import mock
from django.test import TestCase
from neomodel import config, db


class Neo4jTestCase(TestCase):
    """
    Base test case for tests that require Neo4j.
    This class sets up the Neo4j connection with the correct hostname.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test environment before any tests are run."""
        super().setUpClass()
        # Configure Neo4j to use the correct hostname
        config.DATABASE_URL = 'bolt://neo4j:password@neo4j:7687'
        # Clear the Neo4j class registry to avoid duplicate class definitions
        db._NODE_CLASS_REGISTRY = {}

    def setUp(self):
        """Set up the test environment before each test."""
        super().setUp()
        # Ensure the Neo4j connection is configured correctly
        config.DATABASE_URL = 'bolt://neo4j:password@neo4j:7687'


class MockNeo4jTestCase(TestCase):
    """
    Base test case for tests that should mock Neo4j.
    This class mocks the Neo4j connection to avoid needing a real database.
    """

    @classmethod
    def setUpClass(cls):
        """Set up the test environment before any tests are run."""
        super().setUpClass()
        # Start patching neomodel's db module
        cls.db_patcher = mock.patch('neomodel.core.db')
        cls.mock_db = cls.db_patcher.start()

        # Mock the cypher_query method to return empty results
        cls.mock_db.cypher_query.return_value = ([], [])

        # Create a mock instance for GameRuleSet
        cls.mock_rule_set_instance = mock.MagicMock()
        cls.mock_rule_set_instance.name = "Idiot Card Game"
        cls.mock_rule_set_instance.description = "A complex card game with special actions for each card value"
        cls.mock_rule_set_instance.parameters = {
            "deck_configuration": {
                "card_types": ["standard"],
                "suits": ["hearts", "diamonds", "clubs", "spades"],
                "values": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            },
            "dealing_config": {
                "cards_per_player": 4,
                "min_cards": 2,
                "max_cards": 8
            },
            "turn_flow": {
                "initial_direction": "clockwise",
                "can_reverse": True,
                "skip_allowed": True,
                "play_again_allowed": True,
                "chain_actions": True
            },
            "win_conditions": [
                {"type": "empty_hand", "description": "First player to play all cards wins"},
                {"type": "special_last_card", "description": "Special scoring for last card played"}
            ],
            "play_rules": {
                "match_criteria": ["suit", "value"],
                "special_cards": {"J": "choose_suit"},
                "one_card_announcement": {"required": True, "penalty": 1},
                "equal_sum_penalty": {"two_players": -1, "three_players": -3},
                "last_card_special_points": {"2": 3, "J": 2, "7": "continue_if_countered"}
            },
            "card_actions": {
                "hearts_2": {"action_type": "give_card", "target": "next_player"},
                "hearts_7": {"action_type": "draw", "amount": 2, "can_counter": True, "counter_cards": ["8", "10"], "counter_same_suit": True, "chain_action": True},
                "hearts_8": {"action_type": "skip", "target": "next_player", "counter_to": "7", "counter_options": [{"effect": "draw_cards", "target": "next_player", "amount": 5}, {"effect": "draw_cards", "target": "opposite_player", "amount": 2}]},
                "hearts_J": {"action_type": "choose_suit", "effect": "choose_suit", "points_if_last": 2},
                "hearts_A": {"action_type": "play_again", "target": "self", "same_suit": True, "chain_action": True, "chain_with": ["A"]},
                "diamonds_2": {"action_type": "give_card", "target": "next_player"},
                "diamonds_7": {"action_type": "draw", "amount": 2, "can_counter": True, "counter_cards": ["8", "10"], "counter_same_suit": True, "chain_action": True},
                "diamonds_8": {"action_type": "skip", "target": "next_player", "counter_to": "7", "counter_options": [{"effect": "draw_cards", "target": "next_player", "amount": 5}, {"effect": "draw_cards", "target": "opposite_player", "amount": 2}]},
                "diamonds_9": {"action_type": "draw", "target": "all_others", "effect": "draw_cards", "amount": 1},
                "diamonds_J": {"action_type": "choose_suit", "effect": "choose_suit", "points_if_last": 2},
                "diamonds_A": {"action_type": "play_again", "target": "self", "same_suit": True, "chain_action": True, "chain_with": ["A"]},
                "clubs_2": {"action_type": "give_card", "target": "next_player"},
                "clubs_7": {"action_type": "draw", "amount": 2, "can_counter": True, "counter_cards": ["8", "10"], "counter_same_suit": True, "chain_action": True},
                "clubs_8": {"action_type": "skip", "target": "next_player", "counter_to": "7", "counter_options": [{"effect": "draw_cards", "target": "next_player", "amount": 5}, {"effect": "draw_cards", "target": "opposite_player", "amount": 2}]},
                "clubs_J": {"action_type": "choose_suit", "effect": "choose_suit", "points_if_last": 2},
                "clubs_A": {"action_type": "play_again", "target": "self", "same_suit": True, "chain_action": True, "chain_with": ["A"]},
                "spades_2": {"action_type": "give_card", "target": "next_player"},
                "spades_7": {"action_type": "draw", "amount": 2, "can_counter": True, "counter_cards": ["8", "10"], "counter_same_suit": True, "chain_action": True},
                "spades_8": {"action_type": "skip", "target": "next_player", "counter_to": "7", "counter_options": [{"effect": "draw_cards", "target": "next_player", "amount": 5}, {"effect": "draw_cards", "target": "opposite_player", "amount": 2}]},
                "spades_J": {"action_type": "choose_suit", "effect": "choose_suit", "points_if_last": 2},
                "spades_A": {"action_type": "play_again", "target": "self", "same_suit": True, "chain_action": True, "chain_with": ["A"]}
            },
            "targeting_rules": {
                "next_player": {"type": "offset", "offset": 1},
                "previous_player": {"type": "offset", "offset": -1},
                "second_next_player": {"type": "offset", "offset": 2},
                "all": {"type": "all_players"},
                "all_others": {"type": "all_except_current"},
                "self": {"type": "current_player"},
                "player_choice": {"type": "selection", "constraints": ["not_self"]},
                "opposite_player": {"type": "offset", "offset": 2, "min_players": 4}
            }
        }

        # Mock the create_idiot_rule_set function
        cls.create_idiot_rule_set_patcher = mock.patch('backend.game.services.game_service_utils.create_idiot_rule_set.create_idiot_rule_set')
        cls.mock_create_idiot_rule_set = cls.create_idiot_rule_set_patcher.start()
        cls.mock_create_idiot_rule_set.return_value = cls.mock_rule_set_instance

        # Create a custom version for custom parameters
        def mock_create_with_params(*args, **kwargs):
            custom_instance = mock.MagicMock()
            custom_instance.name = "Idiot Card Game"
            custom_instance.description = "A complex card game with special actions for each card value"

            # Copy the default parameters
            custom_instance.parameters = dict(cls.mock_rule_set_instance.parameters)

            # Update with custom parameters
            if 'initial_direction' in kwargs:
                custom_instance.parameters['turn_flow']['initial_direction'] = kwargs['initial_direction']
            if 'cards_per_player' in kwargs:
                custom_instance.parameters['dealing_config']['cards_per_player'] = kwargs['cards_per_player']
            if 'min_cards' in kwargs:
                custom_instance.parameters['dealing_config']['min_cards'] = kwargs['min_cards']
            if 'max_cards' in kwargs:
                custom_instance.parameters['dealing_config']['max_cards'] = kwargs['max_cards']

            return custom_instance

        cls.mock_create_idiot_rule_set.side_effect = mock_create_with_params

    @classmethod
    def tearDownClass(cls):
        """Clean up the test environment after all tests are run."""
        cls.create_idiot_rule_set_patcher.stop()
        cls.db_patcher.stop()
        super().tearDownClass()
