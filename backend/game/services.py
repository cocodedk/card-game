from .models import Game, Player, Card, Deck, GameCard, GameRuleSet, GameAction
import uuid
from datetime import datetime

class GameService:
    """Service for handling game logic and operations"""

    @staticmethod
    def create_game(creator_id, rule_version="1.0"):
        """Create a new game with the specified creator and rule version"""
        # Get the creator player
        creator = Player.nodes.get(user_id=creator_id)

        # Get the rule set
        rule_set = GameRuleSet.nodes.get(version=rule_version)

        # Create the game
        game = Game(
            game_id=str(uuid.uuid4()),
            status='waiting',
            rule_version=rule_version,
            created_at=datetime.now()
        ).save()

        # Connect the creator to the game
        game.players.connect(creator)

        # Connect the rule set to the game
        game.rule_set.connect(rule_set)

        return game

    @staticmethod
    def join_game(game_id, player_id):
        """Add a player to an existing game"""
        game = Game.nodes.get(game_id=game_id)
        player = Player.nodes.get(user_id=player_id)

        # Check if game is in waiting status
        if game.status != 'waiting':
            raise ValueError("Cannot join a game that is not in waiting status")

        # Connect player to game
        game.players.connect(player)

        return game

    @staticmethod
    def start_game(game_id):
        """Start a game that is in waiting status"""
        game = Game.nodes.get(game_id=game_id)

        # Check if game is in waiting status
        if game.status != 'waiting':
            raise ValueError("Cannot start a game that is not in waiting status")

        # Get all players
        players = list(game.players.all())

        # Check if we have enough players
        if len(players) < 2:
            raise ValueError("Need at least 2 players to start a game")

        # Update game status
        game.status = 'in_progress'
        game.started_at = datetime.now()
        game.current_turn = 1
        game.save()

        # Set the first player's turn
        game.current_player.connect(players[0])

        # Initialize game state (this would be more complex in a real implementation)
        # For each player, create their initial hand, deck, etc.
        for player in players:
            # This is a simplified example
            # In a real game, you would deal cards, set up the board, etc.
            pass

        return game

    @staticmethod
    def play_card(game_id, player_id, card_instance_id, target_position):
        """Play a card from a player's hand to the field"""
        game = Game.nodes.get(game_id=game_id)
        player = Player.nodes.get(user_id=player_id)
        card_instance = GameCard.nodes.get(instance_id=card_instance_id)

        # Check if it's the player's turn
        current_player = game.current_player.get()
        if current_player.user_id != player_id:
            raise ValueError("It's not your turn")

        # Check if the card is in the player's hand
        if card_instance.location != 'hand' or card_instance.owner.get().user_id != player_id:
            raise ValueError("Card is not in your hand")

        # Move the card to the field
        card_instance.location = 'field'
        card_instance.position = target_position
        card_instance.save()

        # Record the action
        GameAction(
            action_type='play_card',
            action_data={
                'card_id': card_instance.card.get().card_id,
                'position': target_position
            }
        ).save().game.connect(game).player.connect(player).affected_cards.connect(card_instance)

        return card_instance

    @staticmethod
    def end_turn(game_id, player_id):
        """End the current player's turn and move to the next player"""
        game = Game.nodes.get(game_id=game_id)
        player = Player.nodes.get(user_id=player_id)

        # Check if it's the player's turn
        current_player = game.current_player.get()
        if current_player.user_id != player_id:
            raise ValueError("It's not your turn")

        # Get all players
        players = list(game.players.all())

        # Find the index of the current player
        current_index = next((i for i, p in enumerate(players) if p.user_id == player_id), None)

        # Calculate the next player's index
        next_index = (current_index + 1) % len(players)

        # Update the current player
        game.current_player.disconnect(current_player)
        game.current_player.connect(players[next_index])

        # Increment the turn counter
        game.current_turn += 1
        game.save()

        # Record the action
        GameAction(
            action_type='end_turn',
            action_data={}
        ).save().game.connect(game).player.connect(player)

        return game

    @staticmethod
    def end_game(game_id, winner_id=None):
        """End a game and set the winner if provided"""
        game = Game.nodes.get(game_id=game_id)

        # Update game status
        game.status = 'completed'
        game.ended_at = datetime.now()
        game.save()

        # Set the winner if provided
        if winner_id:
            winner = Player.nodes.get(user_id=winner_id)
            game.winner.connect(winner)

        return game
