from .state_tracker import StateTracker

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
