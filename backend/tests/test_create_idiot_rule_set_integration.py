from backend.tests.fixtures import MockNeo4jTestCase
from unittest.mock import patch, MagicMock

from backend.game.services.game_service_utils.create_idiot_rule_set import create_idiot_rule_set


class CreateIdiotRuleSetIntegrationTests(MockNeo4jTestCase):
    """Integration tests for the create_idiot_rule_set function"""

    @patch('backend.game.models.GameRuleSet.create_idiot_card_game')
    def test_create_idiot_rule_set_integration(self, mock_create_idiot_card_game):
        """Test that the create_idiot_rule_set function creates a valid rule set"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.name = "Idiot Card Game"
        mock_instance.description = "A complex card game with special actions for each card value"
        mock_instance.parameters = {
            "deck_config": {"card_types": ["standard"]},
            "dealing_config": {"cards_per_player": 4},
            "turn_flow": {"initial_direction": "clockwise"},
            "win_conditions": [{"type": "empty_hand"}],
            "play_rules": {"match_criteria": ["suit", "value"]},
            "card_actions": {"hearts_2": {"action_type": "give_card"}},
            "targeting_rules": {"next_player": {"offset": 1}}
        }
        mock_create_idiot_card_game.return_value = mock_instance

        # Call the function
        rule_set = create_idiot_rule_set()

        # Verify that the rule set was created
        self.assertIsNotNone(rule_set)
        self.assertEqual(rule_set.name, "Idiot Card Game")

        # Verify that the rule set has the expected parameters
        self.assertIn("deck_config", rule_set.parameters)
        self.assertIn("dealing_config", rule_set.parameters)
        self.assertIn("turn_flow", rule_set.parameters)
        self.assertIn("win_conditions", rule_set.parameters)
        self.assertIn("play_rules", rule_set.parameters)
        self.assertIn("card_actions", rule_set.parameters)
        self.assertIn("targeting_rules", rule_set.parameters)

    @patch('backend.game.models.GameRuleSet.create_idiot_card_game')
    def test_create_idiot_rule_set_with_custom_parameters(self, mock_create_idiot_card_game):
        """Test creating an idiot rule set with custom parameters"""
        # Setup mock
        mock_instance = MagicMock()
        mock_instance.name = "Idiot Card Game"
        mock_instance.parameters = {
            "turn_flow": {"initial_direction": "counterclockwise"},
            "dealing_config": {
                "cards_per_player": 6,
                "min_cards": 3,
                "max_cards": 10
            }
        }
        mock_create_idiot_card_game.return_value = mock_instance

        # Call the function with custom parameters
        rule_set = create_idiot_rule_set(
            initial_direction="counterclockwise",
            cards_per_player=6,
            min_cards=3,
            max_cards=10
        )

        # Verify that the rule set was created with custom parameters
        self.assertEqual(rule_set.parameters["turn_flow"]["initial_direction"], "counterclockwise")
        self.assertEqual(rule_set.parameters["dealing_config"]["cards_per_player"], 6)
        self.assertEqual(rule_set.parameters["dealing_config"]["min_cards"], 3)
        self.assertEqual(rule_set.parameters["dealing_config"]["max_cards"], 10)

        # Verify the correct parameters were passed to create_idiot_card_game
        args, kwargs = mock_create_idiot_card_game.call_args
        self.assertEqual(kwargs['turn_flow']['initial_direction'], "counterclockwise")
        self.assertEqual(kwargs['dealing_config']['cards_per_player'], 6)
        self.assertEqual(kwargs['dealing_config']['min_cards'], 3)
        self.assertEqual(kwargs['dealing_config']['max_cards'], 10)

    @patch('backend.game.models.GameRuleSet.create_idiot_card_game')
    def test_card_actions_behavior(self, mock_create_idiot_card_game):
        """Test the behavior of card actions in the rule set"""
        # Setup mock
        mock_instance = MagicMock()
        mock_create_idiot_card_game.return_value = mock_instance

        # Call the function
        result = create_idiot_rule_set()

        # Verify card actions in the arguments passed to create_idiot_card_game
        args, kwargs = mock_create_idiot_card_game.call_args
        card_actions = kwargs['card_actions']

        # Check specific card actions
        # 2 of hearts should give a card to the next player
        self.assertEqual(card_actions['hearts_2']['action_type'], 'give_card')
        self.assertEqual(card_actions['hearts_2']['target'], 'next_player')

        # 7 of spades should make next player draw 2 cards and be counterable
        self.assertEqual(card_actions['spades_7']['action_type'], 'draw')
        self.assertEqual(card_actions['spades_7']['amount'], 2)
        self.assertTrue(card_actions['spades_7']['can_counter'])
        self.assertEqual(card_actions['spades_7']['counter_cards'], ['8', '10'])

        # Jack of clubs should allow choosing a suit
        self.assertEqual(card_actions['clubs_J']['action_type'], 'choose_suit')
        self.assertEqual(card_actions['clubs_J']['effect'], 'choose_suit')

        # Ace of diamonds should allow playing again with same suit
        self.assertEqual(card_actions['diamonds_A']['action_type'], 'play_again')
        self.assertEqual(card_actions['diamonds_A']['target'], 'self')
        self.assertTrue(card_actions['diamonds_A']['same_suit'])

    @patch('backend.game.models.GameRuleSet.create_idiot_card_game')
    def test_targeting_rules_behavior(self, mock_create_idiot_card_game):
        """Test the behavior of targeting rules in the rule set"""
        # Setup mock
        mock_instance = MagicMock()
        mock_create_idiot_card_game.return_value = mock_instance

        # Call the function
        result = create_idiot_rule_set()

        # Verify targeting rules in the arguments passed to create_idiot_card_game
        args, kwargs = mock_create_idiot_card_game.call_args
        targeting_rules = kwargs['targeting_rules']

        # Check specific targeting rules
        self.assertEqual(targeting_rules['next_player']['offset'], 1)
        self.assertEqual(targeting_rules['previous_player']['offset'], -1)
        self.assertEqual(targeting_rules['second_next_player']['offset'], 2)
        self.assertEqual(targeting_rules['all']['type'], 'all_players')
        self.assertEqual(targeting_rules['all_others']['type'], 'all_except_current')
