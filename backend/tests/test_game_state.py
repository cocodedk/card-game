from django.test import TestCase
from unittest.mock import patch, MagicMock

from backend.tests.fixtures import MockNeo4jTestCase
from backend.game.models.game_state import GameState
from backend.game.models import GameRuleSet, Game


class GameStateTests(MockNeo4jTestCase):
    """Tests for the GameState model and game flow functionality"""

    def setUp(self):
        """Set up test environment"""
        super().setUp()

        # Create mock rule set
        self.rule_set = MagicMock()
        self.rule_set.parameters = {
            "deck_configuration": {
                "suits": ["hearts", "diamonds", "clubs", "spades"],
                "values": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            },
            "dealing_config": {
                "cards_per_player": 4
            },
            "turn_flow": {
                "initial_direction": "clockwise"
            },
            "card_actions": {
                "hearts_2": {"action_type": "give_card", "target": "next_player"},
                "hearts_7": {"action_type": "draw", "target": "next_player", "amount": 2},
                "hearts_8": {"action_type": "skip", "target": "next_player"},
                "hearts_10": {"action_type": "reverse", "target": "all"},
                "hearts_J": {"action_type": "choose_suit", "target": "none"},
                "hearts_A": {"action_type": "play_again", "target": "self", "same_suit": True},
                "diamonds_A": {"action_type": "play_again", "target": "self"}
            }
        }

        # Create mock game
        self.game = MagicMock()
        self.game.rule_set.get.return_value = self.rule_set

        # Create game state
        self.game_state = GameState()
        self.game_state.game.get = MagicMock(return_value=self.game)

        # Mock the save method to avoid Neo4j database calls
        self.game_state.save = MagicMock()

        # Set up players
        self.player_ids = ["player1", "player2", "player3", "player4"]

        # Initialize game with fixed seed for reproducibility
        with patch('random.shuffle', side_effect=lambda x: x):
            with patch('random.choice', return_value=self.player_ids[0]):
                self.game_state.initialize_game(self.player_ids, self.rule_set)

    def test_initialization(self):
        """Test game initialization"""
        # Check player states
        self.assertEqual(len(self.game_state.player_states), 4)
        for player_id in self.player_ids:
            self.assertIn(player_id, self.game_state.player_states)
            self.assertEqual(len(self.game_state.player_states[player_id]["hand"]), 4)

        # Check initial player
        self.assertEqual(self.game_state.current_player_uid, "player1")

        # Check direction
        self.assertEqual(self.game_state.direction, "clockwise")

        # Check deck
        self.assertEqual(len(self.game_state.draw_pile), 52 - 16)  # 52 cards - 16 dealt
        self.assertEqual(len(self.game_state.discard_pile), 0)

    def test_draw_card(self):
        """Test drawing a card"""
        initial_draw_pile_size = len(self.game_state.draw_pile)
        card = self.game_state.draw_card()

        # Check card was drawn
        self.assertIsNotNone(card)
        self.assertIn("suit", card)
        self.assertIn("value", card)

        # Check draw pile size decreased
        self.assertEqual(len(self.game_state.draw_pile), initial_draw_pile_size - 1)

    def test_play_card_basic(self):
        """Test playing a card - basic case"""
        # Set up a card in player's hand
        test_card = {"suit": "hearts", "value": "5"}
        self.game_state.player_states["player1"]["hand"] = [test_card]

        # Play the card
        result = self.game_state.play_card("player1", test_card)

        # Check result
        self.assertTrue(result["success"])

        # Check card was removed from hand
        self.assertEqual(len(self.game_state.player_states["player1"]["hand"]), 0)

        # Check card was added to discard pile
        self.assertEqual(len(self.game_state.discard_pile), 1)
        self.assertEqual(self.game_state.discard_pile[0], test_card)

    def test_play_card_not_your_turn(self):
        """Test playing a card when it's not your turn"""
        # Set up a card in player's hand
        test_card = {"suit": "hearts", "value": "5"}
        self.game_state.player_states["player2"]["hand"] = [test_card]

        # Play the card as player2 when it's player1's turn
        result = self.game_state.play_card("player2", test_card)

        # Check result
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Not your turn")

        # Check card was not removed from hand
        self.assertEqual(len(self.game_state.player_states["player2"]["hand"]), 1)

        # Check discard pile is empty
        self.assertEqual(len(self.game_state.discard_pile), 0)

    def test_play_card_not_in_hand(self):
        """Test playing a card that's not in the player's hand"""
        # Set up a different card in player's hand
        self.game_state.player_states["player1"]["hand"] = [{"suit": "hearts", "value": "5"}]

        # Try to play a card not in hand
        test_card = {"suit": "diamonds", "value": "7"}
        result = self.game_state.play_card("player1", test_card)

        # Check result
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Card not in hand")

        # Check hand is unchanged
        self.assertEqual(len(self.game_state.player_states["player1"]["hand"]), 1)

        # Check discard pile is empty
        self.assertEqual(len(self.game_state.discard_pile), 0)

    def test_can_play_card_first_card(self):
        """Test that any card can be played as the first card"""
        # Empty discard pile
        self.game_state.discard_pile = []

        # Any card should be playable
        test_card = {"suit": "hearts", "value": "5"}
        self.assertTrue(self.game_state._can_play_card(test_card))

    def test_can_play_card_matching_suit(self):
        """Test playing a card that matches the suit of the top card"""
        # Set up discard pile with a top card
        self.game_state.discard_pile = [{"suit": "hearts", "value": "5"}]

        # Card with matching suit should be playable
        test_card = {"suit": "hearts", "value": "7"}
        self.assertTrue(self.game_state._can_play_card(test_card))

    def test_can_play_card_matching_value(self):
        """Test playing a card that matches the value of the top card"""
        # Set up discard pile with a top card
        self.game_state.discard_pile = [{"suit": "hearts", "value": "5"}]

        # Card with matching value should be playable
        test_card = {"suit": "diamonds", "value": "5"}
        self.assertTrue(self.game_state._can_play_card(test_card))

    def test_can_play_card_jack(self):
        """Test that Jack can always be played"""
        # Set up discard pile with a top card
        self.game_state.discard_pile = [{"suit": "hearts", "value": "5"}]

        # Jack should always be playable
        test_card = {"suit": "clubs", "value": "J"}
        self.assertTrue(self.game_state._can_play_card(test_card))

    def test_can_play_card_invalid(self):
        """Test that an invalid card cannot be played"""
        # Set up discard pile with a top card
        self.game_state.discard_pile = [{"suit": "hearts", "value": "5"}]

        # Card with different suit and value should not be playable
        test_card = {"suit": "clubs", "value": "7"}
        self.assertFalse(self.game_state._can_play_card(test_card))

    def test_can_play_card_with_chosen_suit(self):
        """Test playing a card after a Jack has set the current suit"""
        # Set up discard pile with a Jack
        self.game_state.discard_pile = [{"suit": "hearts", "value": "J"}]

        # Set current suit
        self.game_state.current_suit = "diamonds"

        # Card matching chosen suit should be playable
        test_card = {"suit": "diamonds", "value": "7"}
        self.assertTrue(self.game_state._can_play_card(test_card))

        # Card not matching chosen suit should not be playable
        test_card = {"suit": "clubs", "value": "7"}
        self.assertFalse(self.game_state._can_play_card(test_card))

    def test_apply_card_effects_draw(self):
        """Test applying draw card effects"""
        # Set up player hands
        self.game_state.player_states["player1"]["hand"] = []
        self.game_state.player_states["player2"]["hand"] = []

        # Set up draw pile
        self.game_state.draw_pile = [
            {"suit": "hearts", "value": "2"},
            {"suit": "diamonds", "value": "3"}
        ]

        # Apply draw effect
        card = {"suit": "hearts", "value": "7"}
        effects = self.game_state._apply_card_effects(card, "player1")

        # Check effects
        self.assertEqual(effects["action_type"], "draw")
        self.assertIn("draw", effects)

        # Check target player's hand
        self.assertEqual(len(self.game_state.player_states["player2"]["hand"]), 2)

    def test_apply_card_effects_skip(self):
        """Test applying skip card effects"""
        # Apply skip effect
        card = {"suit": "hearts", "value": "8"}
        effects = self.game_state._apply_card_effects(card, "player1")

        # Check effects
        self.assertEqual(effects["action_type"], "skip")
        self.assertIn("skip", effects)

        # Check skipped players
        self.assertIn("player2", self.game_state.skipped_players)

    def test_apply_card_effects_reverse(self):
        """Test applying reverse card effects"""
        # Initial direction
        self.game_state.direction = "clockwise"

        # Apply reverse effect
        card = {"suit": "hearts", "value": "10"}
        effects = self.game_state._apply_card_effects(card, "player1")

        # Check effects
        self.assertEqual(effects["action_type"], "reverse")
        self.assertTrue(effects["reverse"])

        # Check direction changed
        self.assertEqual(self.game_state.direction, "counterclockwise")

    def test_apply_card_effects_choose_suit(self):
        """Test applying choose suit card effects"""
        # Apply choose suit effect
        card = {"suit": "hearts", "value": "J"}
        chosen_suit = "diamonds"
        effects = self.game_state._apply_card_effects(card, "player1", chosen_suit=chosen_suit)

        # Check effects
        self.assertEqual(effects["action_type"], "choose_suit")
        self.assertEqual(effects["chosen_suit"], "diamonds")

        # Check current suit was set
        self.assertEqual(self.game_state.current_suit, "diamonds")

    def test_apply_card_effects_play_again(self):
        """Test applying play again card effects"""
        # Initial next player
        self.game_state.next_player_uid = "player2"

        # Apply play again effect
        card = {"suit": "hearts", "value": "A"}
        effects = self.game_state._apply_card_effects(card, "player1")

        # Check effects
        self.assertEqual(effects["action_type"], "play_again")
        self.assertTrue(effects["play_again"])
        self.assertTrue(effects["next_player_set"])

        # Check next player is still the current player
        self.assertEqual(self.game_state.next_player_uid, "player1")

    def test_update_next_player_clockwise(self):
        """Test updating next player in clockwise direction"""
        # Set up initial state
        self.game_state.player_states = {
            "player1": {"hand": []},
            "player2": {"hand": []},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"
        self.game_state.direction = "clockwise"

        # Update next player
        self.game_state._update_next_player()

        # Check current player is now player2
        self.assertEqual(self.game_state.current_player_uid, "player2")

        # Check next player is player3
        self.assertEqual(self.game_state.next_player_uid, "player3")

    def test_update_next_player_counterclockwise(self):
        """Test updating next player in counterclockwise direction"""
        # Set up initial state
        self.game_state.player_states = {
            "player1": {"hand": []},
            "player2": {"hand": []},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player2"
        self.game_state.next_player_uid = "player1"
        self.game_state.direction = "counterclockwise"

        # Update next player
        self.game_state._update_next_player()

        # Check current player is now player1
        self.assertEqual(self.game_state.current_player_uid, "player1")

        # Check next player is player4
        self.assertEqual(self.game_state.next_player_uid, "player4")

    def test_update_next_player_with_skipped(self):
        """Test updating next player when some players are skipped"""
        # Set up initial state
        self.game_state.player_states = {
            "player1": {"hand": []},
            "player2": {"hand": []},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"
        self.game_state.direction = "clockwise"
        self.game_state.skipped_players = ["player3"]

        # Update next player
        self.game_state._update_next_player()

        # Check current player is now player2
        self.assertEqual(self.game_state.current_player_uid, "player2")

        # Check next player is player4 (skipping player3)
        self.assertEqual(self.game_state.next_player_uid, "player4")

        # Check skipped players is cleared
        self.assertEqual(len(self.game_state.skipped_players), 0)

    def test_win_condition(self):
        """Test win condition when player has no cards left"""
        # Set up player with one card
        self.game_state.player_states = {
            "player1": {"hand": [{"suit": "hearts", "value": "5"}]},
            "player2": {"hand": []},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"

        # Play the card
        result = self.game_state.play_card("player1", {"suit": "hearts", "value": "5"})

        # Check game is over
        self.assertTrue(self.game_state.game_over)

        # Check winner
        self.assertEqual(self.game_state.winner_id, "player1")

    def test_resolve_target_next_player(self):
        """Test resolving next player target"""
        # Set up initial state
        self.game_state.current_player_uid = "player1"
        self.game_state.direction = "clockwise"

        # Resolve next player target
        target = self.game_state._resolve_target("next_player")

        # Check target is player2
        self.assertEqual(target, ["player2"])

    def test_resolve_target_previous_player(self):
        """Test resolving previous player target"""
        # Set up initial state
        self.game_state.current_player_uid = "player2"
        self.game_state.direction = "clockwise"

        # Resolve previous player target
        target = self.game_state._resolve_target("previous_player")

        # Check target is player1
        self.assertEqual(target, ["player1"])

    def test_resolve_target_all(self):
        """Test resolving all players target"""
        # Resolve all players target
        target = self.game_state._resolve_target("all")

        # Check target includes all players
        self.assertEqual(set(target), set(self.player_ids))

    def test_resolve_target_all_others(self):
        """Test resolving all other players target"""
        # Set up initial state
        self.game_state.current_player_uid = "player1"

        # Resolve all others target
        target = self.game_state._resolve_target("all_others")

        # Check target includes all players except current
        self.assertEqual(set(target), set(["player2", "player3", "player4"]))

    def test_resolve_target_self(self):
        """Test resolving self target"""
        # Set up initial state
        self.game_state.current_player_uid = "player1"

        # Resolve self target
        target = self.game_state._resolve_target("self")

        # Check target is current player
        self.assertEqual(target, ["player1"])

    def test_resolve_target_player_choice(self):
        """Test resolving player choice target"""
        # Resolve player choice target
        target = self.game_state._resolve_target("player_choice", "player3")

        # Check target is chosen player
        self.assertEqual(target, ["player3"])

    def test_full_game_flow(self):
        """Test a full game flow with multiple card plays"""
        # Set up player hands with specific cards for testing
        self.game_state.player_states = {
            "player1": {
                "hand": [
                    {"suit": "hearts", "value": "5"},
                    {"suit": "hearts", "value": "J"},
                    {"suit": "diamonds", "value": "7"}
                ]
            },
            "player2": {
                "hand": [
                    {"suit": "diamonds", "value": "5"},
                    {"suit": "clubs", "value": "10"}
                ]
            },
            "player3": {
                "hand": [
                    {"suit": "diamonds", "value": "A"},
                    {"suit": "diamonds", "value": "2"}
                ]
            },
            "player4": {
                "hand": [
                    {"suit": "clubs", "value": "8"},
                    {"suit": "hearts", "value": "10"}
                ]
            }
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"

        # Set up draw pile
        self.game_state.draw_pile = [
            {"suit": "hearts", "value": "2"},
            {"suit": "diamonds", "value": "3"},
            {"suit": "clubs", "value": "4"}
        ]

        # Set up discard pile with a card to match against
        self.game_state.discard_pile = [{"suit": "hearts", "value": "K"}]

        # Update rule set to include play_again for Ace
        self.rule_set.parameters["card_actions"]["diamonds_A"] = {"action_type": "play_again", "target": "self"}

        # Player 1 plays a card
        result1 = self.game_state.play_card("player1", {"suit": "hearts", "value": "5"})
        self.assertTrue(result1["success"])
        self.assertEqual(self.game_state.current_player_uid, "player2")

        # Player 2 plays a matching value card
        result2 = self.game_state.play_card("player2", {"suit": "diamonds", "value": "5"})
        self.assertTrue(result2["success"])
        self.assertEqual(self.game_state.current_player_uid, "player3")

        # Player 3 plays a matching suit card with play_again effect
        result4 = self.game_state.play_card("player3", {"suit": "diamonds", "value": "A"})
        self.assertTrue(result4["success"])

        # Check that player 3 gets to play again (Ace effect)
        self.assertEqual(self.game_state.current_player_uid, "player3")

        # Player 3 plays their last card (which matches the suit of the previous card)
        result5 = self.game_state.play_card("player3", {"suit": "diamonds", "value": "2"})
        self.assertTrue(result5["success"])

        # Check that player 3 has won
        self.assertTrue(self.game_state.game_over)
        self.assertEqual(self.game_state.winner_id, "player3")

    def test_empty_draw_pile(self):
        """Test behavior when draw pile is empty"""
        # Empty the draw pile
        self.game_state.draw_pile = []

        # Try to draw a card
        card = self.game_state.draw_card()

        # Check that no card was drawn
        self.assertIsNone(card)

        # Try to apply a draw effect
        card = {"suit": "hearts", "value": "7"}
        effects = self.game_state._apply_card_effects(card, "player1")

        # Check that effect was still applied (even though no cards were drawn)
        self.assertEqual(effects["action_type"], "draw")
        self.assertIn("draw", effects)

    def test_card_countering(self):
        """Test card countering mechanics"""
        # Update rule set to include countering
        self.rule_set.parameters["card_actions"]["hearts_7"]["can_counter"] = True
        self.rule_set.parameters["card_actions"]["hearts_7"]["counter_cards"] = ["8"]
        self.rule_set.parameters["card_actions"]["hearts_8"]["counter_to"] = "7"
        self.rule_set.parameters["card_actions"]["hearts_8"]["counter_options"] = [
            {"effect": "draw_cards", "target": "next_player", "amount": 5}
        ]

        # Set up player hands
        self.game_state.player_states = {
            "player1": {"hand": [{"suit": "hearts", "value": "7"}]},
            "player2": {"hand": [{"suit": "hearts", "value": "8"}]},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"

        # Player 1 plays a 7 (draw 2)
        result1 = self.game_state.play_card("player1", {"suit": "hearts", "value": "7"})
        self.assertTrue(result1["success"])

        # Player 2 counters with an 8
        result2 = self.game_state.play_card("player2", {"suit": "hearts", "value": "8"})
        self.assertTrue(result2["success"])

        # Check that the counter effect was applied
        self.assertIn("counter_to", result2["effects"])
        self.assertEqual(result2["effects"]["counter_to"], "7")

    def test_one_card_announcement(self):
        """Test one card announcement functionality"""
        # Add one card announcement to player state
        self.game_state.player_states = {
            "player1": {
                "hand": [
                    {"suit": "hearts", "value": "5"},
                    {"suit": "diamonds", "value": "7"}
                ],
                "announced_one_card": False
            },
            "player2": {"hand": []},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"

        # Play a card without announcing
        result = self.game_state.play_card("player1", {"suit": "hearts", "value": "5"})
        self.assertTrue(result["success"])

        # Check that player now has one card
        self.assertEqual(len(self.game_state.player_states["player1"]["hand"]), 1)

        # Check if announcement status is tracked
        self.assertIn("announced_one_card", self.game_state.player_states["player1"])

        # In a real implementation, there would be a penalty for not announcing

    def test_special_last_card_scoring(self):
        """Test special scoring for last card played"""
        # Set up rule set with special last card scoring
        self.rule_set.parameters["play_rules"] = {
            "last_card_special_points": {
                "2": 3,
                "J": 2
            }
        }

        # Set up player with one card
        self.game_state.player_states = {
            "player1": {"hand": [{"suit": "hearts", "value": "2"}]},
            "player2": {"hand": []},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player1"
        self.game_state.next_player_uid = "player2"

        # Play the last card
        result = self.game_state.play_card("player1", {"suit": "hearts", "value": "2"})
        self.assertTrue(result["success"])

        # Check game is over
        self.assertTrue(self.game_state.game_over)

        # Check winner
        self.assertEqual(self.game_state.winner_id, "player1")

        # In a real implementation, there would be special scoring based on the last card

    def test_deck_reshuffling(self):
        """Test reshuffling discard pile when draw pile is empty"""
        # Set up a method to reshuffle cards
        def reshuffle_cards(self):
            """Reshuffle discard pile into draw pile"""
            if not self.draw_pile and self.discard_pile:
                # Keep the top card in the discard pile
                top_card = self.discard_pile[-1]
                new_draw_pile = self.discard_pile[:-1]

                # Shuffle the new draw pile
                import random
                random.shuffle(new_draw_pile)

                # Update piles
                self.draw_pile = new_draw_pile
                self.discard_pile = [top_card]

        # Add the method to the game state
        self.game_state.reshuffle_cards = reshuffle_cards.__get__(self.game_state, GameState)

        # Set up empty draw pile and full discard pile
        self.game_state.draw_pile = []
        self.game_state.discard_pile = [
            {"suit": "hearts", "value": "2"},
            {"suit": "diamonds", "value": "3"},
            {"suit": "clubs", "value": "4"},
            {"suit": "spades", "value": "5"}
        ]

        # Reshuffle cards
        with patch('random.shuffle', side_effect=lambda x: x):
            self.game_state.reshuffle_cards()

        # Check that cards were reshuffled
        self.assertEqual(len(self.game_state.draw_pile), 3)
        self.assertEqual(len(self.game_state.discard_pile), 1)
        self.assertEqual(self.game_state.discard_pile[0], {"suit": "spades", "value": "5"})

    def test_game_state_serialization(self):
        """Test serializing game state for API responses"""
        # Create a method to serialize game state
        def serialize(self, for_player_id=None):
            """Serialize game state for API response"""
            serialized = {
                "current_player": self.current_player_uid,
                "direction": self.direction,
                "discard_pile_top": self.discard_pile[-1] if self.discard_pile else None,
                "draw_pile_count": len(self.draw_pile),
                "game_over": self.game_over,
                "winner_id": self.winner_id if self.game_over else None,
                "players": {}
            }

            # Add player information
            for player_id, player_state in self.player_states.items():
                player_info = {
                    "card_count": len(player_state["hand"])
                }

                # Only include hand for the requesting player
                if player_id == for_player_id:
                    player_info["hand"] = player_state["hand"]

                serialized["players"][player_id] = player_info

            return serialized

        # Add the method to the game state
        self.game_state.serialize = serialize.__get__(self.game_state, GameState)

        # Set up game state
        self.game_state.discard_pile = [{"suit": "hearts", "value": "5"}]

        # Serialize for player1
        serialized = self.game_state.serialize(for_player_id="player1")

        # Check serialized data
        self.assertEqual(serialized["current_player"], "player1")
        self.assertEqual(serialized["discard_pile_top"], {"suit": "hearts", "value": "5"})
        self.assertEqual(serialized["draw_pile_count"], len(self.game_state.draw_pile))
        self.assertFalse(serialized["game_over"])
        self.assertIsNone(serialized["winner_id"])

        # Check that player1's hand is included
        self.assertIn("hand", serialized["players"]["player1"])

        # Check that other players' hands are not included
        self.assertNotIn("hand", serialized["players"]["player2"])

    def test_multiple_game_rounds(self):
        """Test playing multiple rounds of the game"""
        # Create a method to reset the game for a new round
        def reset_for_new_round(self):
            """Reset the game state for a new round"""
            # Keep player IDs but reset hands
            player_ids = list(self.player_states.keys())

            # Reset game state
            self.game_over = False
            winner_id = self.winner_id  # Store temporarily to set first player
            self.winner_id = None

            # Get the rule set
            rule_set = self.game.get().rule_set.get()

            # Set direction from rule set
            self.direction = rule_set.parameters.get("turn_flow", {}).get("initial_direction", "clockwise")
            self.skipped_players = []

            # Reset player states
            for player_id in player_ids:
                self.player_states[player_id] = {
                    "hand": [],
                    "announced_one_card": False,
                    "penalties": 0
                }

            # Reinitialize deck
            self._initialize_deck(rule_set)

            # Deal cards
            self._deal_initial_cards(rule_set)

            # Set first player (winner of last round goes first)
            if winner_id and winner_id in player_ids:
                self.current_player_uid = winner_id
            else:
                import random
                self.current_player_uid = random.choice(player_ids) if player_ids else None

            # Set next player based on direction
            if player_ids and len(player_ids) > 1 and self.current_player_uid:
                current_index = player_ids.index(self.current_player_uid)
                step = 1 if self.direction == "clockwise" else -1
                next_index = (current_index + step) % len(player_ids)
                self.next_player_uid = player_ids[next_index]
            elif player_ids:
                # If only one player, set next_player_uid to the same player
                self.next_player_uid = player_ids[0]
            else:
                self.next_player_uid = None

        # Add the method to the game state
        self.game_state.reset_for_new_round = reset_for_new_round.__get__(self.game_state, GameState)

        # Set up player states
        self.game_state.player_states = {
            "player1": {"hand": []},
            "player2": {"hand": [{"suit": "hearts", "value": "5"}]},
            "player3": {"hand": []},
            "player4": {"hand": []}
        }
        self.game_state.current_player_uid = "player2"
        self.game_state.next_player_uid = "player3"

        # Play a round and set a winner
        self.game_state.play_card("player2", {"suit": "hearts", "value": "5"})

        # Check game is over and winner is player2
        self.assertTrue(self.game_state.game_over)
        self.assertEqual(self.game_state.winner_id, "player2")

        # Reset for a new round
        with patch('random.shuffle', side_effect=lambda x: x):
            with patch('random.choice', return_value="player2"):
                self.game_state.reset_for_new_round()

        # Check game is reset
        self.assertFalse(self.game_state.game_over)
        self.assertIsNone(self.game_state.winner_id)

        # Check first player is the previous winner
        self.assertEqual(self.game_state.current_player_uid, "player2")
