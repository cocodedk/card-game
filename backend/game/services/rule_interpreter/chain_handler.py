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
