from django.test import TestCase

from backend.game.services.game_service.create_idiot_rule_set import create_idiot_rule_set
from backend.game.models import GameRuleSet


class CreateIdiotRuleSetIntegrationTests(TestCase):
    """Integration tests for the create_idiot_rule_set function"""

    def test_create_idiot_rule_set_integration(self):
        """Test creating an idiot rule set and verify the created object"""
        # Call the function
        rule_set = create_idiot_rule_set()

        # Verify the rule set was created
        self.assertIsInstance(rule_set, GameRuleSet)
        self.assertEqual(rule_set.name, "Idiot Card Game")
        self.assertEqual(rule_set.description, "A complex card game with special actions for each card value")

        # Verify parameters
        params = rule_set.parameters

        # Check deck configuration
        self.assertIn("deck_configuration", params)
        self.assertEqual(params["deck_configuration"]["card_types"], ["standard"])
        self.assertEqual(params["deck_configuration"]["suits"], ["hearts", "diamonds", "clubs", "spades"])

        # Check dealing configuration
        self.assertIn("dealing_config", params)
        self.assertEqual(params["dealing_config"]["cards_per_player"], 4)
        self.assertEqual(params["dealing_config"]["min_cards"], 2)
        self.assertEqual(params["dealing_config"]["max_cards"], 8)

        # Check turn flow
        self.assertIn("turn_flow", params)
        self.assertEqual(params["turn_flow"]["initial_direction"], "clockwise")
        self.assertTrue(params["turn_flow"]["can_reverse"])

        # Check win conditions
        self.assertIn("win_conditions", params)
        self.assertEqual(len(params["win_conditions"]), 2)
        self.assertEqual(params["win_conditions"][0]["type"], "empty_hand")

        # Check card actions
        self.assertIn("card_actions", params)
        self.assertIn("hearts_2", params["card_actions"])
        self.assertIn("diamonds_7", params["card_actions"])
        self.assertIn("clubs_J", params["card_actions"])

    def test_create_idiot_rule_set_with_custom_parameters(self):
        """Test creating an idiot rule set with custom parameters"""
        # Call the function with custom parameters
        rule_set = create_idiot_rule_set(
            initial_direction="counterclockwise",
            cards_per_player=6,
            min_cards=3,
            max_cards=10
        )

        # Verify custom parameters
        params = rule_set.parameters

        # Check turn flow with custom direction
        self.assertEqual(params["turn_flow"]["initial_direction"], "counterclockwise")

        # Check dealing configuration with custom values
        self.assertEqual(params["dealing_config"]["cards_per_player"], 6)
        self.assertEqual(params["dealing_config"]["min_cards"], 3)
        self.assertEqual(params["dealing_config"]["max_cards"], 10)

    def test_card_actions_behavior(self):
        """Test specific card action behaviors in the rule set"""
        # Create the rule set
        rule_set = create_idiot_rule_set()
        params = rule_set.parameters
        card_actions = params["card_actions"]

        # Test 7's draw action and counter mechanism
        hearts_7 = card_actions["hearts_7"]
        self.assertEqual(hearts_7["action_type"], "draw")
        self.assertEqual(hearts_7["amount"], 2)
        self.assertTrue(hearts_7["can_counter"])
        self.assertEqual(hearts_7["counter_cards"], ["8", "10"])
        self.assertTrue(hearts_7["counter_same_suit"])
        self.assertTrue(hearts_7["chain_action"])

        # Test 8's skip action and counter to 7
        spades_8 = card_actions["spades_8"]
        self.assertEqual(spades_8["action_type"], "skip")
        self.assertEqual(spades_8["target"], "next_player")
        self.assertEqual(spades_8["counter_to"], "7")
        self.assertEqual(spades_8["counter_options"][0]["amount"], 5)  # 2+3

        # Test Jack's choose suit action
        diamonds_J = card_actions["diamonds_J"]
        self.assertEqual(diamonds_J["action_type"], "choose_suit")
        self.assertEqual(diamonds_J["effect"], "choose_suit")
        self.assertEqual(diamonds_J["points_if_last"], 2)

        # Test Ace's play again action
        clubs_A = card_actions["clubs_A"]
        self.assertEqual(clubs_A["action_type"], "play_again")
        self.assertEqual(clubs_A["target"], "self")
        self.assertTrue(clubs_A["same_suit"])
        self.assertTrue(clubs_A["chain_action"])
        self.assertEqual(clubs_A["chain_with"], ["A"])

    def test_targeting_rules_behavior(self):
        """Test targeting rules behavior in the rule set"""
        # Create the rule set
        rule_set = create_idiot_rule_set()
        params = rule_set.parameters
        targeting_rules = params["targeting_rules"]

        # Test next player targeting
        self.assertEqual(targeting_rules["next_player"]["offset"], 1)

        # Test previous player targeting
        self.assertEqual(targeting_rules["previous_player"]["offset"], -1)

        # Test second next player targeting
        self.assertEqual(targeting_rules["second_next_player"]["offset"], 2)

        # Test all players targeting
        self.assertEqual(targeting_rules["all"]["type"], "all_players")

        # Test all others targeting
        self.assertEqual(targeting_rules["all_others"]["type"], "all_except_current")

        # Test self targeting
        self.assertEqual(targeting_rules["self"]["type"], "current_player")

        # Test player choice targeting
        self.assertEqual(targeting_rules["player_choice"]["type"], "selection")
        self.assertEqual(targeting_rules["player_choice"]["constraints"], ["not_self"])
