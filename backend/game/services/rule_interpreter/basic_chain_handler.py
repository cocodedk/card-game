from .chain_handler import ChainHandler
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
