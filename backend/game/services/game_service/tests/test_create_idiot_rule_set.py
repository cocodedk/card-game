from django.test import TestCase
from unittest.mock import patch, MagicMock

from backend.game.services.game_service.create_idiot_rule_set import create_idiot_rule_set
from backend.game.models import GameRuleSet


class CreateIdiotRuleSetTests(TestCase):
    """Tests for the create_idiot_rule_set function"""

    @patch('backend.game.services.game_service.create_idiot_rule_set.GameRuleSet')
    def test_create_idiot_rule_set_default_parameters(self, mock_game_rule_set):
        """Test creating an idiot rule set with default parameters"""
        # Setup mock
        mock_instance = MagicMock()
        mock_game_rule_set.create_idiot_card_game.return_value = mock_instance

        # Call the function with default parameters
        result = create_idiot_rule_set()

        # Assertions
        self.assertEqual(result, mock_instance)
        mock_game_rule_set.create_idiot_card_game.assert_called_once()

        # Check that default parameters were used
        args, kwargs = mock_game_rule_set.create_idiot_card_game.call_args
        self.assertEqual(kwargs['name'], "Idiot Card Game")
        self.assertEqual(kwargs['turn_flow']['initial_direction'], "clockwise")
        self.assertEqual(kwargs['dealing_config']['cards_per_player'], 4)
        self.assertEqual(kwargs['dealing_config']['min_cards'], 2)
        self.assertEqual(kwargs['dealing_config']['max_cards'], 8)

    @patch('backend.game.services.game_service.create_idiot_rule_set.GameRuleSet')
    def test_create_idiot_rule_set_custom_parameters(self, mock_game_rule_set):
        """Test creating an idiot rule set with custom parameters"""
        # Setup mock
        mock_instance = MagicMock()
        mock_game_rule_set.create_idiot_card_game.return_value = mock_instance

        # Call the function with custom parameters
        result = create_idiot_rule_set(
            initial_direction="counterclockwise",
            cards_per_player=6,
            min_cards=3,
            max_cards=10
        )

        # Assertions
        self.assertEqual(result, mock_instance)

        # Check that custom parameters were used
        args, kwargs = mock_game_rule_set.create_idiot_card_game.call_args
        self.assertEqual(kwargs['turn_flow']['initial_direction'], "counterclockwise")
        self.assertEqual(kwargs['dealing_config']['cards_per_player'], 6)
        self.assertEqual(kwargs['dealing_config']['min_cards'], 3)
        self.assertEqual(kwargs['dealing_config']['max_cards'], 10)

    @patch('backend.game.services.game_service.create_idiot_rule_set.GameRuleSet')
    def test_card_actions_configuration(self, mock_game_rule_set):
        """Test that card actions are properly configured"""
        # Setup mock
        mock_instance = MagicMock()
        mock_game_rule_set.create_idiot_card_game.return_value = mock_instance

        # Call the function
        result = create_idiot_rule_set()

        # Assertions
        args, kwargs = mock_game_rule_set.create_idiot_card_game.call_args
        card_actions = kwargs['card_actions']

        # Check a few key card actions
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

    @patch('backend.game.services.game_service.create_idiot_rule_set.GameRuleSet')
    def test_targeting_rules_configuration(self, mock_game_rule_set):
        """Test that targeting rules are properly configured"""
        # Setup mock
        mock_instance = MagicMock()
        mock_game_rule_set.create_idiot_card_game.return_value = mock_instance

        # Call the function
        result = create_idiot_rule_set()

        # Assertions
        args, kwargs = mock_game_rule_set.create_idiot_card_game.call_args
        targeting_rules = kwargs['targeting_rules']

        # Check targeting rules
        self.assertEqual(targeting_rules['next_player']['offset'], 1)
        self.assertEqual(targeting_rules['previous_player']['offset'], -1)
        self.assertEqual(targeting_rules['second_next_player']['offset'], 2)
        self.assertEqual(targeting_rules['all']['type'], 'all_players')
        self.assertEqual(targeting_rules['all_others']['type'], 'all_except_current')

    @patch('backend.game.services.game_service.create_idiot_rule_set.GameRuleSet')
    def test_win_conditions_configuration(self, mock_game_rule_set):
        """Test that win conditions are properly configured"""
        # Setup mock
        mock_instance = MagicMock()
        mock_game_rule_set.create_idiot_card_game.return_value = mock_instance

        # Call the function
        result = create_idiot_rule_set()

        # Assertions
        args, kwargs = mock_game_rule_set.create_idiot_card_game.call_args
        win_conditions = kwargs['win_conditions']

        # Check win conditions
        self.assertEqual(len(win_conditions), 2)
        self.assertEqual(win_conditions[0]['type'], 'empty_hand')
        self.assertEqual(win_conditions[1]['type'], 'special_last_card')

    @patch('backend.game.services.game_service.create_idiot_rule_set.GameRuleSet')
    def test_play_rules_configuration(self, mock_game_rule_set):
        """Test that play rules are properly configured"""
        # Setup mock
        mock_instance = MagicMock()
        mock_game_rule_set.create_idiot_card_game.return_value = mock_instance

        # Call the function
        result = create_idiot_rule_set()

        # Assertions
        args, kwargs = mock_game_rule_set.create_idiot_card_game.call_args
        play_rules = kwargs['play_rules']

        # Check play rules
        self.assertEqual(play_rules['match_criteria'], ['suit', 'value'])
        self.assertEqual(play_rules['special_cards']['J'], 'choose_suit')
        self.assertTrue(play_rules['one_card_announcement']['required'])
        self.assertEqual(play_rules['one_card_announcement']['penalty'], 1)
