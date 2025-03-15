from django.test import TestCase

from backend.game.services.game_service.create_idiot_rule_set import create_idiot_rule_set


class GameFlowTests(TestCase):
    """Tests for game flow and turn mechanics in the idiot rule set"""

    def test_turn_flow_configuration(self):
        """Test that turn flow is properly configured"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the turn flow
        turn_flow = rule_set.parameters["turn_flow"]

        # Check turn flow configuration
        self.assertEqual(turn_flow["initial_direction"], "clockwise")
        self.assertTrue(turn_flow["can_reverse"])
        self.assertTrue(turn_flow["skip_allowed"])
        self.assertTrue(turn_flow["play_again_allowed"])
        self.assertTrue(turn_flow["chain_actions"])

    def test_custom_direction(self):
        """Test that custom direction is properly set"""
        # Create the rule set with counterclockwise direction
        rule_set = create_idiot_rule_set(initial_direction="counterclockwise")

        # Get the turn flow
        turn_flow = rule_set.parameters["turn_flow"]

        # Check turn flow configuration
        self.assertEqual(turn_flow["initial_direction"], "counterclockwise")

    def test_win_conditions(self):
        """Test that win conditions are properly configured"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the win conditions
        win_conditions = rule_set.parameters["win_conditions"]

        # Check win conditions
        self.assertEqual(len(win_conditions), 2)

        # First win condition: empty hand
        self.assertEqual(win_conditions[0]["type"], "empty_hand")
        self.assertEqual(win_conditions[0]["description"], "First player to play all cards wins")

        # Second win condition: special last card
        self.assertEqual(win_conditions[1]["type"], "special_last_card")
        self.assertEqual(win_conditions[1]["description"], "Special scoring for last card played")

    def test_play_rules(self):
        """Test that play rules are properly configured"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the play rules
        play_rules = rule_set.parameters["play_rules"]

        # Check match criteria
        self.assertEqual(play_rules["match_criteria"], ["suit", "value"])

        # Check special cards
        self.assertEqual(play_rules["special_cards"]["J"], "choose_suit")

        # Check one card announcement
        self.assertTrue(play_rules["one_card_announcement"]["required"])
        self.assertEqual(play_rules["one_card_announcement"]["penalty"], 1)

        # Check equal sum penalty
        self.assertEqual(play_rules["equal_sum_penalty"]["two_players"], -1)
        self.assertEqual(play_rules["equal_sum_penalty"]["three_players"], -3)

        # Check last card special points
        self.assertEqual(play_rules["last_card_special_points"]["2"], 3)
        self.assertEqual(play_rules["last_card_special_points"]["J"], 2)
        self.assertEqual(play_rules["last_card_special_points"]["7"], "continue_if_countered")

    def test_deck_configuration(self):
        """Test that deck configuration is properly set"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the deck configuration
        deck_config = rule_set.parameters["deck_configuration"]

        # Check deck configuration
        self.assertEqual(deck_config["card_types"], ["standard"])
        self.assertEqual(deck_config["suits"], ["hearts", "diamonds", "clubs", "spades"])
        self.assertEqual(deck_config["values"], ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"])

    def test_dealing_configuration(self):
        """Test that dealing configuration is properly set"""
        # Create the rule set
        rule_set = create_idiot_rule_set()

        # Get the dealing configuration
        dealing_config = rule_set.parameters["dealing_config"]

        # Check dealing configuration
        self.assertEqual(dealing_config["cards_per_player"], 4)
        self.assertEqual(dealing_config["min_cards"], 2)
        self.assertEqual(dealing_config["max_cards"], 8)

        # Test custom dealing configuration
        rule_set = create_idiot_rule_set(cards_per_player=6, min_cards=3, max_cards=10)
        dealing_config = rule_set.parameters["dealing_config"]

        self.assertEqual(dealing_config["cards_per_player"], 6)
        self.assertEqual(dealing_config["min_cards"], 3)
        self.assertEqual(dealing_config["max_cards"], 10)
