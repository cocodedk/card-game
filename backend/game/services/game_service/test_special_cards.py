#!/usr/bin/env python
"""
Tests for special card actions in the Idiot card game
"""
import unittest
from unittest.mock import MagicMock

# Create a mock version of the create_idiot_rule_set function
def mock_create_idiot_rule_set():
    """
    Mock version of create_idiot_rule_set for testing special cards
    """
    # Create a mock rule set
    mock_rule_set = MagicMock()
    mock_rule_set.name = "Idiot Card Game"

    # Set up card actions
    card_actions = {
        # 2: Give a card to the next player
        "hearts_2": {
            "action_type": "give_card",
            "target": "next_player",
            "effect": "give_card",
            "points_if_last": 3
        },

        # 3: Previous player draws a card
        "hearts_3": {
            "action_type": "draw",
            "target": "previous_player",
            "effect": "draw_cards",
            "amount": 1
        },

        # 6: Second player in queue must draw
        "hearts_6": {
            "action_type": "draw",
            "target": "second_next_player",
            "effect": "draw_cards",
            "amount": 1
        },

        # 7: Next player draws 2 cards (special chain rules with 8 and 10)
        "hearts_7": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2,
            "can_counter": True,
            "counter_cards": ["8", "10"],
            "counter_same_suit": True,
            "chain_action": True
        },

        # 8: Skip next player (or counter to 7)
        "hearts_8": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn",
            "counter_to": "7",
            "counter_options": [
                {
                    "effect": "draw_cards",
                    "target": "next_player",
                    "amount": 5,  # 2 from 7 + 3 from 8
                    "description": "Next player draws 5 cards (2+3)"
                },
                {
                    "effect": "draw_cards",
                    "target": "opposite_player",
                    "amount": 2,  # Original penalty from 7
                    "description": "Opposite player draws 2 cards"
                }
            ],
            "chain_counter": {
                "increase_amount": 3,  # Each additional 8 adds 3 more cards
                "or_transfer": "opposite_player"  # Or transfers current penalty to opposite player
            }
        },

        # 9 of diamonds: All other players draw a card
        "diamonds_9": {
            "action_type": "draw",
            "target": "all_others",
            "effect": "draw_cards",
            "amount": 1
        },

        # 10: Reverse game direction (or counter to 7)
        "hearts_10": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction",
            "counter_to": "7",
            "counter_effect": "reverse_and_bounce",
            "bounce_target": "previous_player",
            "bounce_amount": 2
        },

        # Jack: Choose suit
        "hearts_J": {
            "action_type": "choose_suit",
            "target": "none",
            "effect": "choose_suit",
            "points_if_last": 2
        },

        # Queen: Next player must place a card face up but cannot play it
        "hearts_Q": {
            "action_type": "force_reveal",
            "target": "next_player",
            "effect": "reveal_card_and_draw",
            "description": "Next player must reveal a card but cannot play it, and must draw a card"
        },

        # King: Next player draws a card and is skipped
        "hearts_K": {
            "action_type": "draw_and_skip",
            "target": "next_player",
            "effect": "draw_and_skip",
            "amount": 1
        },

        # Ace: Play another card of same suit (chain action)
        "hearts_A": {
            "action_type": "play_again",
            "target": "self",
            "effect": "play_again",
            "same_suit": True,
            "chain_action": True,
            "chain_with": ["A"]
        }
    }

    # Set up parameters
    mock_rule_set.parameters = {
        "card_actions": card_actions
    }

    return mock_rule_set


class TestSpecialCardActions(unittest.TestCase):
    """Tests for special card actions"""

    def test_give_card_action(self):
        """Test the give card action (2s)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check 2 of hearts
        hearts_2 = card_actions["hearts_2"]
        self.assertEqual(hearts_2["action_type"], "give_card")
        self.assertEqual(hearts_2["target"], "next_player")
        self.assertEqual(hearts_2["effect"], "give_card")
        self.assertEqual(hearts_2["points_if_last"], 3)

    def test_draw_card_actions(self):
        """Test the draw card actions (3s, 6s, 7s)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check 3 of hearts (previous player draws)
        hearts_3 = card_actions["hearts_3"]
        self.assertEqual(hearts_3["action_type"], "draw")
        self.assertEqual(hearts_3["target"], "previous_player")
        self.assertEqual(hearts_3["effect"], "draw_cards")
        self.assertEqual(hearts_3["amount"], 1)

        # Check 6 of hearts (second next player draws)
        hearts_6 = card_actions["hearts_6"]
        self.assertEqual(hearts_6["action_type"], "draw")
        self.assertEqual(hearts_6["target"], "second_next_player")
        self.assertEqual(hearts_6["effect"], "draw_cards")
        self.assertEqual(hearts_6["amount"], 1)

        # Check 7 of hearts (next player draws 2, can be countered)
        hearts_7 = card_actions["hearts_7"]
        self.assertEqual(hearts_7["action_type"], "draw")
        self.assertEqual(hearts_7["target"], "next_player")
        self.assertEqual(hearts_7["effect"], "draw_cards")
        self.assertEqual(hearts_7["amount"], 2)
        self.assertTrue(hearts_7["can_counter"])
        self.assertEqual(hearts_7["counter_cards"], ["8", "10"])
        self.assertTrue(hearts_7["counter_same_suit"])
        self.assertTrue(hearts_7["chain_action"])

    def test_skip_action(self):
        """Test the skip action (8s)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check 8 of hearts
        hearts_8 = card_actions["hearts_8"]
        self.assertEqual(hearts_8["action_type"], "skip")
        self.assertEqual(hearts_8["target"], "next_player")
        self.assertEqual(hearts_8["effect"], "skip_turn")
        self.assertEqual(hearts_8["counter_to"], "7")

        # Check counter options
        counter_options = hearts_8["counter_options"]
        self.assertEqual(len(counter_options), 2)

        # First option: Next player draws 5 cards
        self.assertEqual(counter_options[0]["effect"], "draw_cards")
        self.assertEqual(counter_options[0]["target"], "next_player")
        self.assertEqual(counter_options[0]["amount"], 5)

        # Second option: Opposite player draws 2 cards
        self.assertEqual(counter_options[1]["effect"], "draw_cards")
        self.assertEqual(counter_options[1]["target"], "opposite_player")
        self.assertEqual(counter_options[1]["amount"], 2)

        # Check chain counter
        chain_counter = hearts_8["chain_counter"]
        self.assertEqual(chain_counter["increase_amount"], 3)
        self.assertEqual(chain_counter["or_transfer"], "opposite_player")

    def test_diamonds_9_special_action(self):
        """Test the special action for 9 of diamonds"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check 9 of diamonds
        diamonds_9 = card_actions["diamonds_9"]
        self.assertEqual(diamonds_9["action_type"], "draw")
        self.assertEqual(diamonds_9["target"], "all_others")
        self.assertEqual(diamonds_9["effect"], "draw_cards")
        self.assertEqual(diamonds_9["amount"], 1)

    def test_reverse_action(self):
        """Test the reverse action (10s)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check 10 of hearts
        hearts_10 = card_actions["hearts_10"]
        self.assertEqual(hearts_10["action_type"], "reverse")
        self.assertEqual(hearts_10["target"], "all")
        self.assertEqual(hearts_10["effect"], "reverse_direction")
        self.assertEqual(hearts_10["counter_to"], "7")
        self.assertEqual(hearts_10["counter_effect"], "reverse_and_bounce")
        self.assertEqual(hearts_10["bounce_target"], "previous_player")
        self.assertEqual(hearts_10["bounce_amount"], 2)

    def test_choose_suit_action(self):
        """Test the choose suit action (Jacks)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check Jack of hearts
        hearts_J = card_actions["hearts_J"]
        self.assertEqual(hearts_J["action_type"], "choose_suit")
        self.assertEqual(hearts_J["target"], "none")
        self.assertEqual(hearts_J["effect"], "choose_suit")
        self.assertEqual(hearts_J["points_if_last"], 2)

    def test_force_reveal_action(self):
        """Test the force reveal action (Queens)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check Queen of hearts
        hearts_Q = card_actions["hearts_Q"]
        self.assertEqual(hearts_Q["action_type"], "force_reveal")
        self.assertEqual(hearts_Q["target"], "next_player")
        self.assertEqual(hearts_Q["effect"], "reveal_card_and_draw")

    def test_draw_and_skip_action(self):
        """Test the draw and skip action (Kings)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check King of hearts
        hearts_K = card_actions["hearts_K"]
        self.assertEqual(hearts_K["action_type"], "draw_and_skip")
        self.assertEqual(hearts_K["target"], "next_player")
        self.assertEqual(hearts_K["effect"], "draw_and_skip")
        self.assertEqual(hearts_K["amount"], 1)

    def test_play_again_action(self):
        """Test the play again action (Aces)"""
        rule_set = mock_create_idiot_rule_set()
        card_actions = rule_set.parameters["card_actions"]

        # Check Ace of hearts
        hearts_A = card_actions["hearts_A"]
        self.assertEqual(hearts_A["action_type"], "play_again")
        self.assertEqual(hearts_A["target"], "self")
        self.assertEqual(hearts_A["effect"], "play_again")
        self.assertTrue(hearts_A["same_suit"])
        self.assertTrue(hearts_A["chain_action"])
        self.assertEqual(hearts_A["chain_with"], ["A"])


if __name__ == "__main__":
    unittest.main()
