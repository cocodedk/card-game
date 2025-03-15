from django.test import TestCase

from backend.game.services.game_service_utils.create_idiot_rule_set import create_idiot_rule_set


class CreateIdiotRuleSetValidationTests(TestCase):
    """Validation tests for the create_idiot_rule_set function"""

    def test_invalid_initial_direction(self):
        """Test with an invalid initial direction"""
        with self.assertRaises(ValueError):
            create_idiot_rule_set(initial_direction="invalid_direction")

    def test_cards_per_player_out_of_range(self):
        """Test with cards_per_player outside the min/max range"""
        # Test with cards_per_player < min_cards
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=1, min_cards=2)

        # Test with cards_per_player > max_cards
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=10, max_cards=8)

    def test_min_cards_greater_than_max_cards(self):
        """Test with min_cards greater than max_cards"""
        with self.assertRaises(ValueError):
            create_idiot_rule_set(min_cards=6, max_cards=4)

    def test_negative_card_values(self):
        """Test with negative card values"""
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=-1)

        with self.assertRaises(ValueError):
            create_idiot_rule_set(min_cards=-2)

        with self.assertRaises(ValueError):
            create_idiot_rule_set(max_cards=-5)

    def test_zero_cards_per_player(self):
        """Test with zero cards per player"""
        with self.assertRaises(ValueError):
            create_idiot_rule_set(cards_per_player=0)

    def test_boundary_values(self):
        """Test with boundary values"""
        # Test with cards_per_player = min_cards
        rule_set = create_idiot_rule_set(cards_per_player=2, min_cards=2)
        self.assertEqual(rule_set.parameters["dealing_config"]["cards_per_player"], 2)

        # Test with cards_per_player = max_cards
        rule_set = create_idiot_rule_set(cards_per_player=8, max_cards=8)
        self.assertEqual(rule_set.parameters["dealing_config"]["cards_per_player"], 8)
