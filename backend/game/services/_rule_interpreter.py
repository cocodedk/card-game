from abc import ABC, abstractmethod

class GameRuleInterpreter(ABC):
    """Base abstract class for game rule interpreters"""

    def __init__(self, rule_set):
        """
        Initialize with a GameRuleSet instance

        Args:
            rule_set (GameRuleSet): The rule set to interpret
        """
        self.rule_set = rule_set
        self.parameters = rule_set.parameters

    @abstractmethod
    def validate_action(self, game_state, player, action):
        """
        Validate if an action is allowed based on rules

        Args:
            game_state: Current state of the game
            player: Player attempting the action
            action: Action being attempted

        Returns:
            bool: Whether the action is valid
        """
        pass

    @abstractmethod
    def apply_rules(self, game_state):
        """
        Apply rules to the current game state

        Args:
            game_state: Current state of the game

        Returns:
            Updated game state
        """
        pass

    @abstractmethod
    def process_card_play(self, game_state, player, card):
        """
        Process a card being played

        Args:
            game_state: Current state of the game
            player: Player playing the card
            card: Card being played

        Returns:
            Updated game state
        """
        pass


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


# Extension interfaces for game-specific logic

class ChainHandler:
    """Interface for handling chain actions like 7-8-10 sequences"""

    def start_chain(self, game_state, player, card, action_config, targets):
        """Start a new chain action"""
        pass

    def validate_counter(self, game_state, player, card, chain_context):
        """Validate if a card can counter the current chain"""
        pass

    def handle_counter(self, game_state, player, card, action_config, chain_context, targets):
        """Handle a counter card in a chain"""
        pass


class DecisionHandler:
    """Interface for handling player decisions"""

    def resolve_player_choice(self, game_state, player, action_config, target_rule):
        """Resolve a player's choice of target"""
        pass

    def choose_suit(self, game_state, player, action_config):
        """Handle a player choosing a suit (Jack)"""
        pass

    def choose_counter_option(self, game_state, player, card, options):
        """Handle a player choosing between counter options (8)"""
        pass


class StateTracker:
    """Interface for tracking game-specific state"""

    def mark_revealed_card(self, game_state, player, action_config):
        """Mark a card as revealed (can't be played)"""
        pass

    def is_revealed_card(self, game_state, player_uid, card):
        """Check if a card is revealed and can't be played"""
        pass

    def check_one_card_announcement(self, game_state, player_uid):
        """Check if a player announced having one card"""
        pass

    def check_equal_sum_penalty(self, game_state, winner_id):
        """Check for equal sum penalty condition"""
        pass


# Basic implementations of extensions

class BasicChainHandler(ChainHandler):
    """Basic implementation of chain handling"""

    def start_chain(self, game_state, player, card, action_config, targets):
        """Start a new chain action"""
        game_state.chain_context = {
            "initial_card": card.value,
            "initial_suit": card.suit,
            "current_amount": action_config.get("amount", 0),
            "chain_history": [{
                "card_value": card.value,
                "card_suit": card.suit,
                "player_uid": player["id"]
            }]
        }
        return game_state

    def validate_counter(self, game_state, player, card, chain_context):
        """Validate if a card can counter the current chain"""
        initial_card = chain_context.get("initial_card")
        counter_cards = []

        # Find the card action
        card_uid = f"{card.suit}_{card.value}"
        action_config = self.card_actions.get(card_uid, {})

        # Check if this card can counter the initial card
        if action_config.get("counter_to") == initial_card:
            # First counter might need to match suit
            if len(chain_context["chain_history"]) == 1 and action_config.get("counter_same_suit"):
                return card.suit == chain_context["initial_suit"]
            return True

        return False

    def handle_counter(self, game_state, player, card, action_config, chain_context, targets):
        """Handle a counter card in a chain"""
        # Add this card to the chain history
        chain_context["chain_history"].append({
            "card_value": card.value,
            "card_suit": card.suit,
            "player_uid": player["id"]
        })

        # Apply the counter effect
        if action_config.get("counter_effect") == "reverse_and_bounce":
            # Reverse direction and bounce the penalty back
            game_state.direction = "counterclockwise" if game_state.direction == "clockwise" else "clockwise"

            # Find the previous player (who played the card being countered)
            prev_player_uid = chain_context["chain_history"][-2]["player_uid"]
            prev_player = next((p for p in game_state.players if p.id == prev_player_uid), None)

            if prev_player:
                # Make them draw cards
                amount = action_config.get("bounce_amount", chain_context["current_amount"])
                prev_player_state = game_state.player_states.get(prev_player.id)

                if prev_player_state:
                    for _ in range(amount):
                        card = game_state.draw_card()
                        if card:
                            prev_player_state["hand"].append(card)

        return game_state


class BasicDecisionHandler(DecisionHandler):
    """Basic implementation of decision handling"""

    def resolve_player_choice(self, game_state, player, action_config, target_rule):
        """Resolve a player's choice of target"""
        # In a real implementation, this would interact with the UI
        # For now, just return all valid targets
        players = game_state.players
        constraints = target_rule.get("constraints", [])

        if "not_self" in constraints:
            return [p for p in players if p != player]

        return players

    def choose_suit(self, game_state, player, action_config):
        """Handle a player choosing a suit (Jack)"""
        # In a real implementation, this would interact with the UI
        # For now, just return a default suit
        return "hearts"

    def choose_counter_option(self, game_state, player, card, options):
        """Handle a player choosing between counter options (8)"""
        # In a real implementation, this would interact with the UI
        # For now, just return the first option
        if options:
            return options[0]
        return None


class BasicStateTracker(StateTracker):
    """Basic implementation of state tracking"""

    def mark_revealed_card(self, game_state, player, action_config):
        """Mark a card as revealed (can't be played)"""
        # In a real implementation, this would interact with the UI
        # For now, just simulate revealing a random card
        player_state = game_state.player_states.get(player.id)
        if player_state and player_state["hand"]:
            # Reveal the first card
            revealed_card = player_state["hand"][0]

            # Store in game state
            if not hasattr(game_state, "revealed_cards"):
                game_state.revealed_cards = {}

            if player.id not in game_state.revealed_cards:
                game_state.revealed_cards[player.id] = []

            game_state.revealed_cards[player.id].append(revealed_card["id"])

            # Draw a card
            card = game_state.draw_card()
            if card:
                player_state["hand"].append(card)

    def is_revealed_card(self, game_state, player_uid, card):
        """Check if a card is revealed and can't be played"""
        if hasattr(game_state, "revealed_cards") and player_uid in game_state.revealed_cards:
            return card.id in game_state.revealed_cards[player_uid]
        return False

    def check_one_card_announcement(self, game_state, player_uid):
        """Check if a player announced having one card"""
        # In a real implementation, this would check if the player actually announced
        # For now, just return a random result
        import random
        return random.choice([True, False])

    def check_equal_sum_penalty(self, game_state, winner_id):
        """Check for equal sum penalty condition"""
        # In a real implementation, this would calculate card values
        # For now, just return None (no penalty)
        return None


# Idiot-specific implementations

class IdiotChainHandler(ChainHandler):
    """Idiot-specific implementation of chain handling"""

    def start_chain(self, game_state, player, card, action_config, targets):
        """Start a new chain action"""
        game_state.chain_context = {
            "initial_card": card.value,
            "initial_suit": card.suit,
            "current_amount": action_config.get("amount", 0),
            "chain_history": [{
                "card_value": card.value,
                "card_suit": card.suit,
                "player_uid": player["id"]
            }]
        }
        return game_state

    def validate_counter(self, game_state, player, card, chain_context):
        """Validate if a card can counter the current chain"""
        # Get the last card in the chain
        last_card = chain_context["chain_history"][-1]

        # Find the card action
        card_uid = f"{card.suit}_{card.value}"
        action_config = self.card_actions.get(card_uid, {})

        # Check if this card can counter the last card
        counter_to = action_config.get("counter_to")

        if counter_to == "7" and last_card["card_value"] == "7":
            # First counter to 7 must be same suit
            if action_config.get("counter_same_suit"):
                return card.suit == last_card["card_suit"]
            return True

        elif counter_to == "7" and last_card["card_value"] == "8":
            # Counter to an 8 that countered a 7
            # No suit restriction after first counter
            return True

        return False

    def handle_counter(self, game_state, player, card, action_config, chain_context, targets):
        """Handle a counter card in a chain"""
        # Add this card to the chain history
        chain_context["chain_history"].append({
            "card_value": card.value,
            "card_suit": card.suit,
            "player_uid": player["id"]
        })

        # Handle based on the card value
        if card.value == "8":
            # 8 countering a 7 or another 8
            if len(chain_context["chain_history"]) == 2:
                # First 8 in the chain - player chooses between options
                options = action_config.get("counter_options", [])
                choice = self.extensions["decision_handler"].choose_counter_option(
                    game_state, player, card, options
                )

                if choice:
                    # Apply the chosen effect
                    target_type = choice.get("target")
                    effect = choice.get("effect")
                    amount = choice.get("amount", 0)

                    # Resolve the target
                    target_players = []
                    if target_type == "next_player":
                        current_index = game_state.players.index(player)
                        next_index = (current_index + 1) % len(game_state.players)
                        target_players = [game_state.players[next_index]]
                    elif target_type == "opposite_player":
                        current_index = game_state.players.index(player)
                        opposite_index = (current_index + (len(game_state.players) // 2)) % len(game_state.players)
                        target_players = [game_state.players[opposite_index]]

                    # Apply the effect
                    if effect == "draw_cards" and target_players:
                        for target in target_players:
                            target_state = game_state.player_states.get(target.id)
                            if target_state:
                                for _ in range(amount):
                                    card = game_state.draw_card()
                                    if card:
                                        target_state["hand"].append(card)
            else:
                # Subsequent 8 in the chain - player chooses to increase or transfer
                chain_counter = action_config.get("chain_counter", {})

                # In a real implementation, this would interact with the UI
                # For now, just randomly choose
                import random
                if random.choice([True, False]):
                    # Increase the penalty
                    increase_amount = chain_counter.get("increase_amount", 3)
                    chain_context["current_amount"] += increase_amount
                else:
                    # Transfer to opposite player
                    current_index = game_state.players.index(player)
                    opposite_index = (current_index + (len(game_state.players) // 2)) % len(game_state.players)
                    opposite_player = game_state.players[opposite_index]

                    # Make them draw cards
                    opposite_state = game_state.player_states.get(opposite_player.id)
                    if opposite_state:
                        for _ in range(chain_context["current_amount"]):
                            card = game_state.draw_card()
                            if card:
                                opposite_state["hand"].append(card)

                    # Reset the chain
                    game_state.chain_context = None

        elif card.value == "10":
            # 10 countering a 7
            # Reverse direction and bounce the penalty back
            game_state.direction = "counterclockwise" if game_state.direction == "clockwise" else "clockwise"

            # Find the previous player (who played the 7)
            prev_player_uid = chain_context["chain_history"][-2]["player_uid"]
            prev_player = next((p for p in game_state.players if p.id == prev_player_uid), None)

            if prev_player:
                # Make them draw cards
                amount = action_config.get("bounce_amount", chain_context["current_amount"])
                prev_player_state = game_state.player_states.get(prev_player.id)

                if prev_player_state:
                    for _ in range(amount):
                        card = game_state.draw_card()
                        if card:
                            prev_player_state["hand"].append(card)

            # Reset the chain
            game_state.chain_context = None


class IdiotDecisionHandler(DecisionHandler):
    """Idiot-specific implementation of decision handling"""

    def resolve_player_choice(self, game_state, player, action_config, target_rule):
        """Resolve a player's choice of target"""
        # In a real implementation, this would interact with the UI
        # For now, just return all valid targets
        players = game_state.players
        constraints = target_rule.get("constraints", [])

        if "not_self" in constraints:
            return [p for p in players if p != player]

        return players

    def choose_suit(self, game_state, player, action_config):
        """Handle a player choosing a suit (Jack)"""
        # In a real implementation, this would interact with the UI
        # For now, just return a default suit
        return "hearts"

    def choose_counter_option(self, game_state, player, card, options):
        """Handle a player choosing between counter options (8)"""
        # In a real implementation, this would interact with the UI
        # For now, just return the first option
        if options:
            return options[0]
        return None


class IdiotStateTracker(StateTracker):
    """Idiot-specific implementation of state tracking"""

    def mark_revealed_card(self, game_state, player, action_config):
        """Mark a card as revealed (can't be played)"""
        player_state = game_state.player_states.get(player.id)
        if player_state and player_state["hand"]:
            # For Queen effect: player must reveal a card but can't play it
            # In a real implementation, this would interact with the UI
            # For now, just reveal the first card
            revealed_card = player_state["hand"][0]

            # Store in game state
            if not hasattr(game_state, "revealed_cards"):
                game_state.revealed_cards = {}

            if player.id not in game_state.revealed_cards:
                game_state.revealed_cards[player.id] = []

            game_state.revealed_cards[player.id].append(revealed_card["id"])

            # Draw a card
            card = game_state.draw_card()
            if card:
                player_state["hand"].append(card)

    def is_revealed_card(self, game_state, player_uid, card):
        """Check if a card is revealed and can't be played"""
        if hasattr(game_state, "revealed_cards") and player_uid in game_state.revealed_cards:
            return card.id in game_state.revealed_cards[player_uid]
        return False

    def check_one_card_announcement(self, game_state, player_uid):
        """Check if a player announced having one card"""
        # In a real implementation, this would check if the player actually announced
        # For now, just return a random result
        import random
        return random.choice([True, False])

    def check_equal_sum_penalty(self, game_state, winner_id):
        """
        Check for equal sum penalty condition

        In Idiot game:
        - If two players' cards sum to equal values, winner loses 1 point
        - If three players' cards sum to equal values, winner loses 3 points
        """
        # Calculate card values for each player
        player_sums = {}
        for player_uid, player_state in game_state.player_states.items():
            if player_uid != winner_id:  # Skip the winner
                total = 0
                for card in player_state["hand"]:
                    # Convert face cards to numeric values
                    value = card["value"]
                    if value == "J":
                        total += 11
                    elif value == "Q":
                        total += 12
                    elif value == "K":
                        total += 13
                    elif value == "A":
                        total += 14
                    else:
                        try:
                            total += int(value)
                        except ValueError:
                            total += 10  # Default for non-numeric values

                player_sums[player_uid] = total

        # Check for equal sums
        values = list(player_sums.values())
        if len(values) >= 2:
            # Check if any two players have equal sums
            for i in range(len(values)):
                for j in range(i+1, len(values)):
                    if values[i] == values[j]:
                        # Two players have equal sums
                        return -1

        if len(values) >= 3:
            # Check if any three players have equal sums
            for i in range(len(values)):
                for j in range(i+1, len(values)):
                    for k in range(j+1, len(values)):
                        if values[i] == values[j] == values[k]:
                            # Three players have equal sums
                            return -3

        return None


def get_rule_interpreter(rule_set):
    """
    Factory function to get the appropriate rule interpreter

    Args:
        rule_set (GameRuleSet): The rule set to interpret

    Returns:
        GameRuleInterpreter: An appropriate interpreter instance
    """
    game_type = rule_set.version.split('-')[0]

    if game_type == "action_cards":
        return ActionCardRuleInterpreter(rule_set)
    elif game_type == "idiot_cards":
        return ActionCardRuleInterpreter(rule_set)  # Uses the same interpreter with different extensions
    else:
        raise ValueError(f"No interpreter available for game type: {game_type}")
