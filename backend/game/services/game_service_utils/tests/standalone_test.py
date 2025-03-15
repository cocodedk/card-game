#!/usr/bin/env python
"""
Standalone test for create_idiot_rule_set
"""
import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, '/app')

# Mock the GameRuleSet class
class MockGameRuleSet:
    """Mock GameRuleSet for testing"""

    @classmethod
    def create_idiot_card_game(cls, **kwargs):
        """Mock create_idiot_card_game method"""
        mock_rule_set = MockRuleSet()
        mock_rule_set.name = kwargs.get('name')
        mock_rule_set.description = kwargs.get('description')
        mock_rule_set.parameters = kwargs
        return mock_rule_set


class MockRuleSet:
    """Mock rule set object"""

    def __init__(self):
        self.name = None
        self.description = None
        self.parameters = {}

    def save(self):
        """Mock save method"""
        return self


# Mock the GameRuleSet import
sys.modules['backend.game.models'] = MagicMock()
sys.modules['backend.game.models'].GameRuleSet = MockGameRuleSet

# Now import the function to test
from backend.game.services.game_service_utils.create_idiot_rule_set import create_idiot_rule_set


class TestCreateIdiotRuleSet(unittest.TestCase):
    """Tests for create_idiot_rule_set function"""

    def test_default_parameters(self):
        """Test with default parameters"""
        rule_set = create_idiot_rule_set()

        # Check basic properties
        self.assertEqual(rule_set.name, "Idiot Card Game")
        self.assertEqual(rule_set.description, "A complex card game with special actions for each card value")

        # Check turn flow
        self.assertEqual(rule_set.parameters["turn_flow"]["initial_direction"], "clockwise")

        # Check dealing config
        self.assertEqual(rule_set.parameters["dealing_config"]["cards_per_player"], 4)
        self.assertEqual(rule_set.parameters["dealing_config"]["min_cards"], 2)
        self.assertEqual(rule_set.parameters["dealing_config"]["max_cards"], 8)

    def test_custom_parameters(self):
        """Test with custom parameters"""
        rule_set = create_idiot_rule_set(
            initial_direction="counterclockwise",
            cards_per_player=6,
            min_cards=3,
            max_cards=10
        )

        # Check custom parameters
        self.assertEqual(rule_set.parameters["turn_flow"]["initial_direction"], "counterclockwise")
        self.assertEqual(rule_set.parameters["dealing_config"]["cards_per_player"], 6)
        self.assertEqual(rule_set.parameters["dealing_config"]["min_cards"], 3)
        self.assertEqual(rule_set.parameters["dealing_config"]["max_cards"], 10)

    def test_card_actions(self):
        """Test card actions"""
        rule_set = create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check 2 of hearts
        self.assertEqual(card_actions["hearts_2"]["action_type"], "give_card")
        self.assertEqual(card_actions["hearts_2"]["target"], "next_player")

        # Check 7 of spades
        self.assertEqual(card_actions["spades_7"]["action_type"], "draw")
        self.assertEqual(card_actions["spades_7"]["amount"], 2)
        self.assertTrue(card_actions["spades_7"]["can_counter"])

        # Check Jack of clubs
        self.assertEqual(card_actions["clubs_J"]["action_type"], "choose_suit")

        # Check 9 of diamonds (special case)
        self.assertEqual(card_actions["diamonds_9"]["action_type"], "draw")
        self.assertEqual(card_actions["diamonds_9"]["target"], "all_others")

    def test_validation(self):
        """Test validation logic"""
        # Test invalid direction
        with self.assertRaises(ValueError):
            create_idiot_rule_set(initial_direction="invalid")

        # Test cards_per_player < min_cards
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=1, min_cards=2)

        # Test cards_per_player > max_cards
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=10, max_cards=8)

        # Test min_cards > max_cards
        with self.assertRaises(ValueError):
            create_idiot_rule_set(min_cards=6, max_cards=4)

        # Test negative values
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=-1)

        # Test zero cards
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=0)


if __name__ == "__main__":
    unittest.main()
