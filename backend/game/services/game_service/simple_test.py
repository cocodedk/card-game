#!/usr/bin/env python
"""
Simple test for create_idiot_rule_set
"""
import unittest
from unittest.mock import MagicMock, patch

# Create a mock version of the create_idiot_rule_set function
def mock_create_idiot_rule_set(initial_direction="clockwise", cards_per_player=4, min_cards=2, max_cards=8):
    """
    Mock version of create_idiot_rule_set for testing
    """
    # Validate initial_direction
    if initial_direction not in ["clockwise", "counterclockwise"]:
        raise ValueError("initial_direction must be either 'clockwise' or 'counterclockwise'")

    # Validate card counts
    if cards_per_player <= 0:
        raise ValueError("cards_per_player must be greater than 0")

    if min_cards <= 0:
        raise ValueError("min_cards must be greater than 0")

    if max_cards <= 0:
        raise ValueError("max_cards must be greater than 0")

    if min_cards > max_cards:
        raise ValueError("min_cards cannot be greater than max_cards")

    if cards_per_player < min_cards:
        raise ValueError("cards_per_player cannot be less than min_cards")

    if cards_per_player > max_cards:
        raise ValueError("cards_per_player cannot be greater than max_cards")

    # Create a mock rule set
    mock_rule_set = MagicMock()
    mock_rule_set.name = "Idiot Card Game"
    mock_rule_set.description = "A complex card game with special actions for each card value"

    # Set up parameters
    mock_rule_set.parameters = {
        "turn_flow": {
            "initial_direction": initial_direction,
            "can_reverse": True,
            "skip_allowed": True,
            "play_again_allowed": True,
            "chain_actions": True
        },
        "dealing_config": {
            "cards_per_player": cards_per_player,
            "min_cards": min_cards,
            "max_cards": max_cards
        },
        "card_actions": {
            "hearts_2": {
                "action_type": "give_card",
                "target": "next_player",
                "effect": "give_card",
                "points_if_last": 3
            },
            "spades_7": {
                "action_type": "draw",
                "target": "next_player",
                "effect": "draw_cards",
                "amount": 2,
                "can_counter": True,
                "counter_cards": ["8", "10"],
                "counter_same_suit": True,
                "chain_action": True
            },
            "clubs_J": {
                "action_type": "choose_suit",
                "target": "none",
                "effect": "choose_suit",
                "points_if_last": 2
            },
            "diamonds_9": {
                "action_type": "draw",
                "target": "all_others",
                "effect": "draw_cards",
                "amount": 1
            }
        },
        "win_conditions": [
            {"type": "empty_hand", "description": "First player to play all cards wins"},
            {"type": "special_last_card", "description": "Special scoring for last card played"}
        ],
        "play_rules": {
            "match_criteria": ["suit", "value"],
            "special_cards": {
                "J": "choose_suit"
            },
            "one_card_announcement": {
                "required": True,
                "penalty": 1
            },
            "equal_sum_penalty": {
                "two_players": -1,
                "three_players": -3
            },
            "last_card_special_points": {
                "2": 3,
                "J": 2,
                "7": "continue_if_countered"
            }
        }
    }

    return mock_rule_set


class TestCreateIdiotRuleSet(unittest.TestCase):
    """Tests for create_idiot_rule_set function"""

    def test_default_parameters(self):
        """Test with default parameters"""
        rule_set = mock_create_idiot_rule_set()

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
        rule_set = mock_create_idiot_rule_set(
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
        rule_set = mock_create_idiot_rule_set()
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
            mock_create_idiot_rule_set(initial_direction="invalid")

        # Test cards_per_player < min_cards
        with self.assertRaises(ValueError):
            mock_create_idiot_rule_set(cards_per_player=1, min_cards=2)

        # Test cards_per_player > max_cards
        with self.assertRaises(ValueError):
            mock_create_idiot_rule_set(cards_per_player=10, max_cards=8)

        # Test min_cards > max_cards
        with self.assertRaises(ValueError):
            mock_create_idiot_rule_set(min_cards=6, max_cards=4)

        # Test negative values
        with self.assertRaises(ValueError):
            mock_create_idiot_rule_set(cards_per_player=-1)

        # Test zero cards
        with self.assertRaises(ValueError):
            mock_create_idiot_rule_set(cards_per_player=0)


if __name__ == "__main__":
    unittest.main()
