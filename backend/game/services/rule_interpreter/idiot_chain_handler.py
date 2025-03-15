from .chain_handler import ChainHandler
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
