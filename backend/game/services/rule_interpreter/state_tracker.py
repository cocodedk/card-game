
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
