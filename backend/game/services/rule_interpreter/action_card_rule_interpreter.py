from .game_rule_interpreter import GameRuleInterpreter
from .basic_chain_handler import BasicChainHandler
from .basic_decision_handler import BasicDecisionHandler
from .basic_state_tracker import BasicStateTracker
from .idiot_chain_handler import IdiotChainHandler
from .idiot_decision_handler import IdiotDecisionHandler
from .idiot_state_tracker import IdiotStateTracker

class ActionCardRuleInterpreter(GameRuleInterpreter):
    """Rule interpreter for action card games with extension points for complex rules"""

    def __init__(self, rule_set):
        super().__init__(rule_set)
        self.card_actions = self.parameters.get("card_actions", {})
        self.targeting_rules = self.parameters.get("targeting_rules", {})
        self.turn_flow = self.parameters.get("turn_flow", {})
        self.win_conditions = self.parameters.get("win_conditions", [])
        self.play_rules = self.parameters.get("play_rules", {})

        # Initialize game-specific extensions
        self.extensions = {}
        self._register_extensions()

    def _register_extensions(self):
        """Register game-specific extensions based on rule set type"""
        game_type = self.rule_set.version.split('-')[0]

        if game_type == "action_cards":
            # Basic action card extensions
            self.extensions["chain_handler"] = BasicChainHandler()
            self.extensions["decision_handler"] = BasicDecisionHandler()
            self.extensions["state_tracker"] = BasicStateTracker()

        if game_type == "idiot_cards":
            # Idiot-specific extensions
            self.extensions["chain_handler"] = IdiotChainHandler()
            self.extensions["decision_handler"] = IdiotDecisionHandler()
            self.extensions["state_tracker"] = IdiotStateTracker()

    def get_card_action(self, card):
        """
        Get the action for a specific card

        Args:
            card: Card object with suit and value properties

        Returns:
            dict: Action configuration for the card
        """
        card_uid = f"{card.suit}_{card.value}"
        return self.card_actions.get(card_uid)

    def resolve_target(self, game_state, player, action_config):
        """
        Determine the target player(s) based on targeting rules

        Args:
            game_state: Current state of the game
            player: Player playing the card
            action_config: Action configuration from the card

        Returns:
            list: List of target players
        """
        target_type = action_config.get("target")
        target_rule = self.targeting_rules.get(target_type, {})

        players = game_state.players
        current_index = players.index(player)
        total_players = len(players)

        if target_type == "next_player":
            offset = target_rule.get("offset", 1)
            target_index = (current_index + offset) % total_players
            return [players[target_index]]

        elif target_type == "previous_player":
            offset = target_rule.get("offset", 1)
            target_index = (current_index - offset) % total_players
            return [players[target_index]]

        elif target_type == "second_next_player":
            offset = target_rule.get("offset", 2)
            target_index = (current_index + offset) % total_players
            return [players[target_index]]

        elif target_type == "opposite_player":
            target_index = (current_index + (total_players // 2)) % total_players
            return [players[target_index]]

        elif target_type == "all":
            return players

        elif target_type == "all_others":
            return [p for p in players if p != player]

        elif target_type == "self":
            return [player]

        elif target_type == "none":
            return []

        elif target_type == "player_choice":
            # This would be handled by the decision handler
            return self.extensions["decision_handler"].resolve_player_choice(
                game_state, player, action_config, target_rule
            )

        return []

    def apply_card_effect(self, game_state, player, card, targets):
        """
        Apply the effect of a card to the targets

        Args:
            game_state: Current state of the game
            player: Player playing the card
            card: Card being played
            targets: List of target players

        Returns:
            Updated game state
        """
        action_config = self.get_card_action(card)
        if not action_config:
            return game_state

        effect = action_config.get("effect")

        # Check if this is part of a chain action
        chain_context = game_state.chain_context if hasattr(game_state, "chain_context") else None

        if chain_context and action_config.get("counter_to"):
            # This is a counter card in a chain
            return self.extensions["chain_handler"].handle_counter(
                game_state, player, card, action_config, chain_context, targets
            )

        # Handle standard effects
        if effect == "skip_turn":
            for target in targets:
                game_state.skipped_players.append(target.id)

        elif effect == "reverse_direction":
            game_state.direction = "counterclockwise" if game_state.direction == "clockwise" else "clockwise"

        elif effect == "draw_cards":
            amount = action_config.get("amount", 1)
            for target in targets:
                for _ in range(amount):
                    card = game_state.draw_card()
                    if card:
                        target_state = game_state.player_states.get(target.id)
                        if target_state:
                            target_state["hand"].append(card)

        elif effect == "give_card":
            # Implementation for giving a card to another player
            # This would need UI interaction to select which card to give
            pass

        elif effect == "choose_suit":
            # Set the current suit for next play
            game_state.current_suit = self.extensions["decision_handler"].choose_suit(
                game_state, player, action_config
            )

        elif effect == "reveal_card_and_draw":
            # Queen effect: reveal a card but can't play it
            for target in targets:
                self.extensions["state_tracker"].mark_revealed_card(
                    game_state, target, action_config
                )

        elif effect == "draw_and_skip":
            # King effect: draw and skip
            amount = action_config.get("amount", 1)
            for target in targets:
                for _ in range(amount):
                    card = game_state.draw_card()
                    if card:
                        target_state = game_state.player_states.get(target.id)
                        if target_state:
                            target_state["hand"].append(card)
                game_state.skipped_players.append(target.id)

        elif effect == "play_again":
            # Ace effect: play another card
            game_state.play_again = player.id
            game_state.play_again_constraints = {
                "same_suit": action_config.get("same_suit", False),
                "chain_with": action_config.get("chain_with", [])
            }

        # Check if this card starts a chain action
        if action_config.get("chain_action"):
            game_state = self.extensions["chain_handler"].start_chain(
                game_state, player, card, action_config, targets
            )

        return game_state

    def validate_action(self, game_state, player_state, action):
        """
        Validate if playing a card is allowed

        Args:
            game_state: Current state of the game
            player_state: State of the player attempting to play
            action: Action object with type and card properties

        Returns:
            bool: Whether the action is valid
        """
        if action.type != "play_card":
            return False

        card = action.card

        # Check if player has the card
        if card not in player_state["hand"]:
            return False

        # Check if it's a play_again action
        if hasattr(game_state, "play_again") and game_state.play_again == player_state["id"]:
            constraints = getattr(game_state, "play_again_constraints", {})

            # Check if the card meets the constraints
            if constraints.get("same_suit") and hasattr(game_state, "last_card"):
                if card.suit != game_state.last_card.suit:
                    return False

            if constraints.get("chain_with") and card.value not in constraints["chain_with"]:
                # Can only chain with specific cards (like Aces)
                if card.value not in constraints["chain_with"]:
                    return False

            return True

        # Check if the card is a revealed card that can't be played (Queen effect)
        if self.extensions["state_tracker"].is_revealed_card(game_state, player_state["id"], card):
            return False

        # Check if it's a counter to a chain action
        chain_context = getattr(game_state, "chain_context", None)
        if chain_context:
            return self.extensions["chain_handler"].validate_counter(
                game_state, player_state, card, chain_context
            )

        # Normal play - check if the card matches the top card
        top_card = game_state.discard_pile[-1] if game_state.discard_pile else None

        if top_card:
            # Get match criteria from play rules
            match_criteria = self.play_rules.get("match_criteria", ["suit", "value"])

            # Check if there's a current suit set by a Jack
            current_suit = getattr(game_state, "current_suit", None)

            if "suit" in match_criteria:
                if current_suit:
                    # Match against the chosen suit
                    if card.suit != current_suit and card.value != "J":
                        return False
                else:
                    # Match against the top card's suit
                    if card.suit != top_card["suit"] and card.value != top_card["value"]:
                        # Special cards like Jack can be played anytime
                        special_cards = self.play_rules.get("special_cards", {})
                        if card.value not in special_cards:
                            return False

            elif "value" in match_criteria and card.value != top_card["value"]:
                return False

        return True

    def apply_rules(self, game_state):
        """
        Apply game rules after an action

        Args:
            game_state: Current state of the game

        Returns:
            Updated game state
        """
        # Check one-card announcement
        one_card_rule = self.play_rules.get("one_card_announcement", {})
        if one_card_rule.get("required"):
            for player_uid, player_state in game_state.player_states.items():
                if len(player_state["hand"]) == 1 and not player_state.get("announced_one_card"):
                    # Player has one card but hasn't announced it
                    if self.extensions["state_tracker"].check_one_card_announcement(
                        game_state, player_uid
                    ):
                        # Player announced correctly
                        player_state["announced_one_card"] = True
                    else:
                        # Player didn't announce - apply penalty
                        penalty = one_card_rule.get("penalty", 1)
                        for _ in range(penalty):
                            card = game_state.draw_card()
                            if card:
                                player_state["hand"].append(card)

        # Check win conditions
        for player_uid, player_state in game_state.player_states.items():
            for win_condition in self.win_conditions:
                if win_condition["type"] == "empty_hand" and len(player_state["hand"]) == 0:
                    # Check for special last card rules
                    if hasattr(game_state, "last_card") and hasattr(game_state, "last_player"):
                        last_card = game_state.last_card

                        # Check for equal sum penalty
                        equal_sum_penalty = self.play_rules.get("equal_sum_penalty", {})
                        if equal_sum_penalty:
                            penalty = self.extensions["state_tracker"].check_equal_sum_penalty(
                                game_state, player_uid
                            )
                            if penalty:
                                player_state["score"] += penalty

                        # Check for special last card points
                        special_points = self.play_rules.get("last_card_special_points", {})
                        if last_card.value in special_points:
                            points = special_points[last_card.value]
                            if isinstance(points, int):
                                player_state["score"] += points
                            elif points == "continue_if_countered" and last_card.value == "7":
                                # Special case for 7 as last card
                                if not getattr(game_state, "countered_last_7", False):
                                    game_state.winner_id = player_uid
                                    game_state.game_over = True
                    else:
                        game_state.winner_id = player_uid
                        game_state.game_over = True

        # Determine next player based on turn flow
        if not game_state.game_over:
            # Check if current player gets to play again
            if hasattr(game_state, "play_again") and game_state.play_again:
                game_state.next_player_uid = game_state.play_again
                game_state.play_again = None
                game_state.play_again_constraints = None
            else:
                current_index = game_state.players.index(game_state.current_player)
                direction_modifier = 1 if game_state.direction == "clockwise" else -1

                next_index = (current_index + direction_modifier) % len(game_state.players)
                next_player = game_state.players[next_index]

                # Skip players if needed
                while next_player.id in game_state.skipped_players:
                    game_state.skipped_players.remove(next_player.id)
                    next_index = (next_index + direction_modifier) % len(game_state.players)
                    next_player = game_state.players[next_index]

                game_state.next_player_uid = next_player.id

        return game_state

    def process_card_play(self, game_state, player_state, card):
        """
        Process a card being played

        Args:
            game_state: Current state of the game
            player_state: State of the player playing the card
            card: Card being played

        Returns:
            Updated game state
        """
        # Remove card from player's hand
        player_state["hand"] = [c for c in player_state["hand"] if c["id"] != card.id]

        # Add to discard pile
        game_state.discard_pile.append({
            "id": card.id,
            "suit": card.suit,
            "value": card.value
        })

        # Store last card and player for win condition checking
        game_state.last_card = card
        game_state.last_player = player_state["id"]

        # Get card action
        action_config = self.get_card_action(card)
        if action_config:
            # Determine targets
            targets = self.resolve_target(game_state, player_state, action_config)

            # Apply effect
            game_state = self.apply_card_effect(game_state, player_state, card, targets)

        return game_state
