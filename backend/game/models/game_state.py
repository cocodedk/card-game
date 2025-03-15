from neomodel import (
    StringProperty, ArrayProperty, JSONProperty, RelationshipTo, BooleanProperty
)
from backend.game.models.base import GameBaseModel

class GameState(GameBaseModel):
    """Model to store the current state of a game"""
    current_player_uid = StringProperty(index=True)
    next_player_uid = StringProperty()
    direction = StringProperty(default="clockwise")
    skipped_players = ArrayProperty(StringProperty())
    discard_pile = JSONProperty(default=[])
    draw_pile = JSONProperty(default=[])
    player_states = JSONProperty(default={})
    game_over = BooleanProperty(default=False)
    winner_id = StringProperty()
    current_suit = StringProperty()  # For tracking chosen suit from Jack

    # Relationships
    game = RelationshipTo('backend.game.models.game.Game', 'STATE_OF')

    @property
    def current_player(self):
        """Get the current player object"""
        return self.player_states.get(self.current_player_uid, {})

    @property
    def players(self):
        """Get all player objects"""
        return [self.player_states[pid] for pid in self.player_states]

    def draw_card(self):
        """Draw a card from the draw pile"""
        # Check if draw pile is empty and needs reshuffling
        if not self.draw_pile:
            self.reshuffle_cards()

        # If still empty after reshuffling, return None
        if not self.draw_pile:
            return None

        return self.draw_pile.pop(0)

    def play_card(self, player_id, card, target_player_id=None, chosen_suit=None):
        """
        Play a card from a player's hand

        Args:
            player_id: ID of the player playing the card
            card: Card object or dictionary with suit and value
            target_player_id: ID of the target player for targeted actions
            chosen_suit: Chosen suit when playing a Jack

        Returns:
            dict: Result of the play including effects applied
        """
        # Validate it's the player's turn
        if player_id != self.current_player_uid:
            return {"success": False, "message": "Not your turn"}

        # Validate the card is in the player's hand
        player = self.player_states[player_id]
        if card not in player["hand"]:
            return {"success": False, "message": "Card not in hand"}

        # Validate the card can be played (matches top discard or is special)
        if not self._can_play_card(card):
            return {"success": False, "message": "Invalid card play"}

        # Remove card from player's hand
        player["hand"].remove(card)
        self.player_states[player_id] = player

        # Add card to discard pile
        self.discard_pile.append(card)

        # Apply card effects
        effects = self._apply_card_effects(card, player_id, target_player_id, chosen_suit)

        # Check for win condition
        if len(player["hand"]) == 0:
            self.game_over = True
            self.winner_id = player_id

        # Update next player if not determined by card effects
        if "next_player_set" not in effects:
            self._update_next_player()

        self.save()
        return {"success": True, "effects": effects}

    def _can_play_card(self, card):
        """Check if a card can be played based on game rules"""
        if not self.discard_pile:
            return True  # First card can always be played

        top_card = self.discard_pile[-1]

        # Get current suit (might be chosen by Jack)
        current_suit = self.current_suit if hasattr(self, "current_suit") and self.current_suit else top_card["suit"]

        # Card matches suit or value
        if card["suit"] == current_suit or card["value"] == top_card["value"]:
            return True

        # Jack can always be played (choose suit)
        if card["value"] == "J":
            return True

        return False

    def _apply_card_effects(self, card, player_id, target_player_id=None, chosen_suit=None):
        """Apply effects of the played card"""
        # Get rule set to determine card actions
        rule_set = self.game.get().rule_set.get()
        card_key = f"{card['suit'].lower()}_{card['value']}"

        # Get card action from rule set
        card_actions = rule_set.parameters.get("card_actions", {})
        action = card_actions.get(card_key, {})

        effects = {"action_type": action.get("action_type")}

        # Handle different action types
        if action.get("action_type") == "draw":
            self._handle_draw_action(action, target_player_id)
            effects["draw"] = {"target": target_player_id, "amount": action.get("amount", 1)}

        elif action.get("action_type") == "skip":
            self._handle_skip_action(action, target_player_id)
            effects["skip"] = {"target": target_player_id}

            # Check if this is a counter to another card
            if action.get("counter_to"):
                effects["counter_to"] = action.get("counter_to")

        elif action.get("action_type") == "reverse":
            self._handle_reverse_action()
            effects["reverse"] = True

        elif action.get("action_type") == "choose_suit":
            if chosen_suit:
                self.current_suit = chosen_suit
                effects["chosen_suit"] = chosen_suit

        elif action.get("action_type") == "play_again":
            # Don't update next player, same player goes again
            effects["play_again"] = True
            effects["next_player_set"] = True
            self.next_player_uid = player_id

        elif action.get("action_type") == "give_card":
            self._handle_give_card_action(action, player_id, target_player_id)
            effects["give_card"] = {"target": target_player_id}

        return effects

    def _update_next_player(self):
        """Update the next player based on current direction and skipped players"""
        players = list(self.player_states.keys()) if self.player_states else []

        # If no players, return early
        if not players:
            return

        # If current_player_uid is not set, set it to the first player
        if not self.current_player_uid and players:
            self.current_player_uid = players[0]

        # If next_player_uid is not set, set it to the second player or first if only one player
        if not self.next_player_uid and players:
            if len(players) > 1:
                self.next_player_uid = players[1]
            else:
                self.next_player_uid = players[0]
            return

        # Update current player to next player
        self.current_player_uid = self.next_player_uid

        # Find the current player's index
        current_index = players.index(self.current_player_uid) if self.current_player_uid in players else 0

        # Determine step direction
        step = 1 if self.direction == "clockwise" else -1

        # Find next player who isn't skipped
        next_index = current_index
        while True:
            next_index = (next_index + step) % len(players)
            if players[next_index] not in self.skipped_players:
                break

        # Update next player
        self.next_player_uid = players[next_index]

        # Clear skipped players for next round
        self.skipped_players = []

    def initialize_game(self, player_ids, rule_set):
        """Initialize a new game with players and rule set"""
        # Setup player states
        self.player_states = {}
        for player_id in player_ids:
            self.player_states[player_id] = {
                "hand": [],
                "announced_one_card": False,
                "penalties": 0
            }

        # Initialize deck based on rule set
        self._initialize_deck(rule_set)

        # Deal cards to players
        self._deal_initial_cards(rule_set)

        # Set first player randomly
        import random
        self.current_player_uid = random.choice(player_ids) if player_ids else None

        # Set initial direction from rule set
        self.direction = rule_set.parameters.get("turn_flow", {}).get("initial_direction", "clockwise")

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

        # Clear skipped players
        self.skipped_players = []

    def _initialize_deck(self, rule_set):
        """Initialize and shuffle the deck based on rule set"""
        # Create cards based on rule set configuration
        deck = []
        suits = rule_set.parameters.get("deck_configuration", {}).get("suits", [])
        values = rule_set.parameters.get("deck_configuration", {}).get("values", [])

        for suit in suits:
            for value in values:
                deck.append({"suit": suit, "value": value})

        # Shuffle deck
        import random
        random.shuffle(deck)

        self.draw_pile = deck
        self.discard_pile = []

    def _deal_initial_cards(self, rule_set):
        """Deal initial cards to players based on rule set"""
        cards_per_player = rule_set.parameters.get("dealing_config", {}).get("cards_per_player", 4)

        for player_id in self.player_states:
            for _ in range(cards_per_player):
                card = self.draw_card()
                if card:
                    self.player_states[player_id]["hand"].append(card)

    def _handle_draw_action(self, action, target_player_id):
        """Handle draw card action"""
        amount = action.get("amount", 1)
        target = self._resolve_target(action.get("target"), target_player_id)

        for player_id in target:
            for _ in range(amount):
                card = self.draw_card()
                if card:
                    self.player_states[player_id]["hand"].append(card)

    def _handle_skip_action(self, action, target_player_id):
        """Handle skip player action"""
        target = self._resolve_target(action.get("target"), target_player_id)
        self.skipped_players.extend(target)

    def _handle_reverse_action(self):
        """Handle direction reversal"""
        self.direction = "counterclockwise" if self.direction == "clockwise" else "clockwise"

    def _handle_give_card_action(self, action, player_id, target_player_id):
        """Handle giving a card to another player"""
        target = self._resolve_target(action.get("target"), target_player_id)

        # If no valid target, return
        if not target:
            return

        # Get a random card from the draw pile
        card = self.draw_card()
        if not card:
            return

        # Add the card to the target player's hand
        for target_id in target:
            self.player_states[target_id]["hand"].append(card)

    def _resolve_target(self, target_type, specific_target=None):
        """Resolve target based on targeting rules"""
        players = list(self.player_states.keys())
        current_index = players.index(self.current_player_uid)

        if target_type == "next_player":
            step = 1 if self.direction == "clockwise" else -1
            return [players[(current_index + step) % len(players)]]

        elif target_type == "previous_player":
            step = -1 if self.direction == "clockwise" else 1
            return [players[(current_index + step) % len(players)]]

        elif target_type == "second_next_player":
            step = 2 if self.direction == "clockwise" else -2
            return [players[(current_index + step) % len(players)]]

        elif target_type == "all":
            return players

        elif target_type == "all_others":
            return [p for p in players if p != self.current_player_uid]

        elif target_type == "self":
            return [self.current_player_uid]

        elif target_type == "player_choice" and specific_target:
            return [specific_target]

        return []

    def reshuffle_cards(self):
        """Reshuffle discard pile into draw pile when draw pile is empty"""
        if not self.draw_pile and len(self.discard_pile) > 1:
            # Keep the top card in the discard pile
            top_card = self.discard_pile[-1]
            new_draw_pile = self.discard_pile[:-1]

            # Shuffle the new draw pile
            import random
            random.shuffle(new_draw_pile)

            # Update piles
            self.draw_pile = new_draw_pile
            self.discard_pile = [top_card]

    def serialize(self, for_player_id=None):
        """
        Serialize game state for API response

        Args:
            for_player_id: ID of the player requesting the state (to show their hand)

        Returns:
            dict: Serialized game state
        """
        serialized = {
            "current_player": self.current_player_uid,
            "direction": self.direction,
            "discard_pile_top": self.discard_pile[-1] if self.discard_pile else None,
            "draw_pile_count": len(self.draw_pile),
            "game_over": self.game_over,
            "winner_id": self.winner_id if self.game_over else None,
            "players": {}
        }

        # Add current suit if set (from Jack)
        if hasattr(self, "current_suit") and self.current_suit:
            serialized["current_suit"] = self.current_suit

        # Add player information
        for player_id, player_state in self.player_states.items():
            player_info = {
                "card_count": len(player_state["hand"]),
                "announced_one_card": player_state.get("announced_one_card", False),
                "penalties": player_state.get("penalties", 0)
            }

            # Only include hand for the requesting player
            if player_id == for_player_id:
                player_info["hand"] = player_state["hand"]

            serialized["players"][player_id] = player_info

        return serialized

    def reset_for_new_round(self):
        """Reset the game state for a new round"""
        # Keep player IDs but reset hands
        player_ids = list(self.player_states.keys())

        # Reset game state
        self.game_over = False
        winner_id = self.winner_id  # Store temporarily to set first player
        self.winner_id = None
        self.direction = self.game.get().rule_set.get().parameters.get("turn_flow", {}).get("initial_direction", "clockwise")
        self.skipped_players = []
        self.current_suit = None

        # Reset player states
        for player_id in player_ids:
            self.player_states[player_id] = {
                "hand": [],
                "announced_one_card": False,
                "penalties": 0
            }

        # Reinitialize deck
        self._initialize_deck(self.game.get().rule_set.get())

        # Deal cards
        self._deal_initial_cards(self.game.get().rule_set.get())

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

        self.save()
