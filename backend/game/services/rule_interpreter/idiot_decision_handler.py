from .decision_handler import DecisionHandler

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
