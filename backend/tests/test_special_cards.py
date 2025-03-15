from unittest.mock import patch
from backend.tests.fixtures import Neo4jTestCase
from backend.game.services.game_service_utils.create_idiot_rule_set import create_idiot_rule_set


class SpecialCardTests(Neo4jTestCase):
    """Tests for special card actions in the idiot rule set"""

    def test_nine_of_diamonds_special_action(self):
        """Test that 9 of diamonds has a special action affecting all other players"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the card actions
        card_actions = rule_set.parameters["card_actions"]

        # Check that 9 of diamonds has a special action
        self.assertIn("diamonds_9", card_actions)
        diamonds_9 = card_actions["diamonds_9"]

        # Verify the special action
        self.assertEqual(diamonds_9["action_type"], "draw")
        self.assertEqual(diamonds_9["target"], "all_others")
        self.assertEqual(diamonds_9["effect"], "draw_cards")
        self.assertEqual(diamonds_9["amount"], 1)

        # Verify that other 9s don't have this special action
        self.assertNotIn("action_type", card_actions.get("hearts_9", {}))
        self.assertNotIn("action_type", card_actions.get("clubs_9", {}))
        self.assertNotIn("action_type", card_actions.get("spades_9", {}))

    def test_jack_choose_suit_action(self):
        """Test that all Jacks allow choosing a suit"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the card actions
        card_actions = rule_set.parameters["card_actions"]

        # Check all Jacks
        jack_cards = ["hearts_J", "diamonds_J", "clubs_J", "spades_J"]

        for jack in jack_cards:
            self.assertIn(jack, card_actions)
            self.assertEqual(card_actions[jack]["action_type"], "choose_suit")
            self.assertEqual(card_actions[jack]["effect"], "choose_suit")
            self.assertEqual(card_actions[jack]["points_if_last"], 2)

    def test_seven_counter_mechanism(self):
        """Test that 7s can be countered by 8s and 10s"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the card actions
        card_actions = rule_set.parameters["card_actions"]

        # Check all 7s
        seven_cards = ["hearts_7", "diamonds_7", "clubs_7", "spades_7"]

        for seven in seven_cards:
            self.assertIn(seven, card_actions)
            self.assertTrue(card_actions[seven]["can_counter"])
            self.assertEqual(card_actions[seven]["counter_cards"], ["8", "10"])
            self.assertTrue(card_actions[seven]["counter_same_suit"])
            self.assertTrue(card_actions[seven]["chain_action"])

    def test_eight_counter_options(self):
        """Test that 8s have counter options for 7s"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the card actions
        card_actions = rule_set.parameters["card_actions"]

        # Check all 8s
        eight_cards = ["hearts_8", "diamonds_8", "clubs_8", "spades_8"]

        for eight in eight_cards:
            self.assertIn(eight, card_actions)
            self.assertEqual(card_actions[eight]["counter_to"], "7")

            # Check counter options
            counter_options = card_actions[eight]["counter_options"]
            self.assertEqual(len(counter_options), 2)

            # First option: Next player draws 5 cards
            self.assertEqual(counter_options[0]["effect"], "draw_cards")
            self.assertEqual(counter_options[0]["target"], "next_player")
            self.assertEqual(counter_options[0]["amount"], 5)

            # Second option: Opposite player draws 2 cards
            self.assertEqual(counter_options[1]["effect"], "draw_cards")
            self.assertEqual(counter_options[1]["target"], "opposite_player")
            self.assertEqual(counter_options[1]["amount"], 2)
