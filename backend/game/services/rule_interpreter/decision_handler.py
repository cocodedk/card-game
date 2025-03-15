
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
