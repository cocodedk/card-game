from datetime import datetime
from backend.game.models import Game, GameState, GameCard, GameAction, Player
from backend.game.services.rule_interpreter.base import get_rule_interpreter
from backend.game.services.game_service_utils.action import Action

def play_card(game_uid, player_uid, card_uid):
    """
    Handle a player playing a card

    Args:
        game_uid (str): ID of the game
        player_uid (str): ID of the player
        card_uid (str): ID of the card (GameCard uid)

    Returns:
        dict: Result of the action
    """
    try:
        # Get the game
        game = Game.nodes.get(uid=game_uid)

        # Check game status
        if game.status != "in_progress":
            return {"error": "Game is not active"}

        # Get the rule set
        rule_set = game.rule_set.single()

        # Get the rule interpreter
        interpreter = get_rule_interpreter(rule_set)

        # Get the game state
        game_state = GameState.nodes.filter(game=game).first()
        if not game_state:
            return {"error": "Game state not found"}

        # Check if it's the player's turn
        if game_state.current_player_uid != player_uid:
            return {"error": "Not your turn"}

        # Get the player
        player = Player.nodes.get(uid=player_uid)
        player_state = game_state.player_states.get(player_uid)
        if not player_state:
            return {"error": "Player not found in game state"}

        # Get the game card
        game_card = GameCard.nodes.get(uid=card_uid)

        # Find the card in player's hand
        card_data = next((c for c in player_state["hand"] if c["uid"] == card_uid), None)
        if not card_data:
            return {"error": "Card not in player's hand"}

        # Create card object for validation
        class CardObj:
            def __init__(self, uid, suit, value):
                self.uid = uid
                self.suit = suit
                self.value = value

            def __eq__(self, other):
                if not isinstance(other, CardObj) and not isinstance(other, dict):
                    return False
                if isinstance(other, dict):
                    return self.uid == other.get("uid")
                return self.uid == other.uid

        card_obj = CardObj(card_data["uid"], card_data["suit"], card_data["value"])
        action = Action(type="play_card", card=card_obj)

        # Validate the action
        if interpreter.validate_action(game_state, player_state, action):
            # Process the card play
            updated_state = interpreter.process_card_play(game_state, player_state, card_obj)

            # Apply any additional rules
            final_state = interpreter.apply_rules(updated_state)

            # Update the game card location
            game_card.location = 'field'
            game_card.save()

            # Record the action
            GameAction(
                action_type="play_card",
                action_data={
                    "card_uid": card_uid,
                    "player_uid": player_uid,
                    "card_suit": card_data["suit"],
                    "card_value": card_data["value"]
                }
            ).save().game.connect(game).player.connect(player).affected_cards.connect(game_card)

            # Save the updated state - transfer all relevant properties
            # Core properties
            game_state.current_player_uid = final_state.current_player_uid
            game_state.next_player_uid = final_state.next_player_uid
            game_state.direction = final_state.direction
            game_state.skipped_players = final_state.skipped_players
            game_state.discard_pile = final_state.discard_pile
            game_state.draw_pile = final_state.draw_pile
            game_state.player_states = final_state.player_states
            game_state.game_over = final_state.game_over
            game_state.winner_id = final_state.winner_id

            # Special properties for complex games
            if hasattr(final_state, "revealed_cards"):
                game_state.revealed_cards = final_state.revealed_cards

            if hasattr(final_state, "current_suit"):
                game_state.current_suit = final_state.current_suit

            if hasattr(final_state, "chain_context"):
                game_state.chain_context = final_state.chain_context

            if hasattr(final_state, "last_card"):
                game_state.last_card = {
                    "id": final_state.last_card.id,
                    "suit": final_state.last_card.suit,
                    "value": final_state.last_card.value
                }

            if hasattr(final_state, "last_player"):
                game_state.last_player = final_state.last_player

            game_state.save()

            # Check if game is over
            if final_state.game_over:
                game.status = "completed"
                if final_state.winner_id:
                    winner = Player.nodes.get(uid=final_state.winner_id)
                    game.winner.connect(winner)
                game.completed_at = datetime.now()
                game.ended_at = datetime.now()
                game.save()

                return {
                    "success": True,
                    "game_over": True,
                    "winner": final_state.winner_id
                }

            # Update current player
            next_player = Player.nodes.get(uid=final_state.next_player_uid)
            game.current_player.disconnect_all()
            game.current_player.connect(next_player)

            # Update game state
            game_state.current_player_uid = final_state.next_player_uid
            game_state.next_player_uid = None
            game_state.save()

            return {
                "success": True,
                "next_player": final_state.next_player_uid
            }
        else:
            return {"error": "Invalid card play"}

    except Exception as e:
        # Log the error
        print(f"Error in play_card: {str(e)}")
        return {"error": f"An error occurred: {str(e)}"}
