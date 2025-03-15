from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from backend.game.models import Game, GameState
from backend.game.models.player import Player
from .notifications import GameNotifications


class GameActionView(APIView):
    """Base view for game actions"""

    def get_game_and_validate_player(self, request, game_id):
        """
        Get game and validate that the requesting user is a player in the game

        Args:
            request: The request object
            game_id: The ID of the game

        Returns:
            tuple: (game, player, game_state) or None if validation fails
        """
        # Get the game
        game = get_object_or_404(Game, uid=game_id)

        # Get the player
        player = get_object_or_404(Player, user=request.user)

        # Check if player is in the game
        if player.uid not in game.players:
            return Response(
                {"error": "You are not a player in this game"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get the game state
        game_state = game.state.get()

        return game, player, game_state


class PlayCardView(GameActionView):
    """View for playing a card"""

    def post(self, request, game_id):
        """
        Play a card

        Args:
            request: The request object with card data
            game_id: The ID of the game

        Returns:
            Response: The result of the card play
        """
        # Validate request data
        card = request.data.get("card")
        target_player_id = request.data.get("target_player_id")
        chosen_suit = request.data.get("chosen_suit")

        if not card:
            return Response(
                {"error": "Card data is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get game and validate player
        result = self.get_game_and_validate_player(request, game_id)
        if isinstance(result, Response):
            return result

        game, player, game_state = result

        # Check if it's the player's turn
        if game_state.current_player_uid != player.uid:
            return Response(
                {"error": "It's not your turn"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Play the card
        result = game_state.play_card(
            player_id=player.uid,
            card=card,
            target_player_id=target_player_id,
            chosen_suit=chosen_suit
        )

        # Return the result
        if result["success"]:
            # Send notification
            GameNotifications.notify_card_played(
                game_id=game.uid,
                player_id=player.uid,
                card=card,
                effects=result.get("effects", {})
            )

            # If the turn changed, send a notification
            if "next_player" in result.get("effects", {}):
                GameNotifications.notify_turn_changed(
                    game_id=game.uid,
                    player_id=result["effects"]["next_player"]
                )

            # Get updated game state for the player
            serialized_state = game_state.serialize(for_player_id=player.uid)
            return Response({
                "success": True,
                "effects": result.get("effects", {}),
                "game_state": serialized_state
            })
        else:
            return Response({
                "success": False,
                "message": result.get("message", "Failed to play card")
            }, status=status.HTTP_400_BAD_REQUEST)


class DrawCardView(GameActionView):
    """View for drawing a card"""

    def post(self, request, game_id):
        """
        Draw a card

        Args:
            request: The request object
            game_id: The ID of the game

        Returns:
            Response: The result of drawing a card
        """
        # Get game and validate player
        result = self.get_game_and_validate_player(request, game_id)
        if isinstance(result, Response):
            return result

        game, player, game_state = result

        # Check if it's the player's turn
        if game_state.current_player_uid != player.uid:
            return Response(
                {"error": "It's not your turn"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Draw a card
        card = game_state.draw_card()

        if card:
            # Add card to player's hand
            game_state.player_states[player.uid]["hand"].append(card)
            game_state.save()

            # Send notification
            GameNotifications.notify_card_drawn(
                game_id=game.uid,
                player_id=player.uid
            )

            # Get updated game state for the player
            serialized_state = game_state.serialize(for_player_id=player.uid)

            return Response({
                "success": True,
                "card": card,
                "game_state": serialized_state
            })
        else:
            return Response({
                "success": False,
                "message": "No cards left to draw"
            }, status=status.HTTP_400_BAD_REQUEST)


class AnnounceOneCardView(GameActionView):
    """View for announcing one card"""

    def post(self, request, game_id):
        """
        Announce that player has one card left

        Args:
            request: The request object
            game_id: The ID of the game

        Returns:
            Response: The result of the announcement
        """
        # Get game and validate player
        result = self.get_game_and_validate_player(request, game_id)
        if isinstance(result, Response):
            return result

        game, player, game_state = result

        # Check if player has exactly one card
        player_hand = game_state.player_states[player.uid]["hand"]
        if len(player_hand) != 1:
            return Response({
                "success": False,
                "message": "You don't have exactly one card"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Set announced_one_card flag
        game_state.player_states[player.uid]["announced_one_card"] = True
        game_state.save()

        # Send notification
        GameNotifications.notify_one_card_announced(
            game_id=game.uid,
            player_id=player.uid
        )

        return Response({
            "success": True,
            "message": "One card announced successfully"
        })


class GetGameStateView(GameActionView):
    """View for getting the current game state"""

    def get(self, request, game_id):
        """
        Get the current game state

        Args:
            request: The request object
            game_id: The ID of the game

        Returns:
            Response: The current game state
        """
        # Get game and validate player
        result = self.get_game_and_validate_player(request, game_id)
        if isinstance(result, Response):
            return result

        game, player, game_state = result

        # Get serialized game state for the player
        serialized_state = game_state.serialize(for_player_id=player.uid)

        return Response(serialized_state)


class CreateGameView(APIView):
    """View for creating a new game"""

    def post(self, request):
        """
        Create a new game

        Args:
            request: The request object with game settings

        Returns:
            Response: The created game data
        """
        # Get the player
        player = get_object_or_404(Player, user=request.user)

        # Get rule set ID from request
        rule_set_id = request.data.get("rule_set_id")
        if not rule_set_id:
            return Response({
                "error": "Rule set ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create the game
        game = Game.create_game(
            creator_id=player.uid,
            rule_set_id=rule_set_id,
            name=request.data.get("name", "Idiot Card Game")
        )

        return Response({
            "success": True,
            "game_id": game.uid,
            "message": "Game created successfully"
        }, status=status.HTTP_201_CREATED)


class JoinGameView(APIView):
    """View for joining a game"""

    def post(self, request, game_id):
        """
        Join a game

        Args:
            request: The request object
            game_id: The ID of the game to join

        Returns:
            Response: The result of joining the game
        """
        # Get the game
        game = get_object_or_404(Game, uid=game_id)

        # Get the player
        player = get_object_or_404(Player, user=request.user)

        # Check if player is already in the game
        if player.uid in game.players:
            return Response({
                "success": True,
                "message": "You are already in this game"
            })

        # Check if game is full
        max_players = game.rule_set.get().parameters.get("max_players", 4)
        if len(game.players) >= max_players:
            return Response({
                "error": "Game is full"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Add player to the game
        game.add_player(player.uid)

        # Send notification
        GameNotifications.notify_player_joined(
            game_id=game.uid,
            player_id=player.uid,
            player_name=player.username
        )

        return Response({
            "success": True,
            "message": "Joined game successfully"
        })


class StartGameView(GameActionView):
    """View for starting a game"""

    def post(self, request, game_id):
        """
        Start a game

        Args:
            request: The request object
            game_id: The ID of the game to start

        Returns:
            Response: The result of starting the game
        """
        # Get game and validate player
        result = self.get_game_and_validate_player(request, game_id)
        if isinstance(result, Response):
            return result

        game, player, game_state = result

        # Check if player is the creator
        if game.creator_id != player.uid:
            return Response({
                "error": "Only the game creator can start the game"
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if game has enough players
        min_players = game.rule_set.get().parameters.get("min_players", 2)
        if len(game.players) < min_players:
            return Response({
                "error": f"Need at least {min_players} players to start"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Initialize game state
        game_state.initialize_game(game.players, game.rule_set.get())
        game_state.save()

        # Update game status
        game.status = "active"
        game.save()

        # Send notification
        GameNotifications.notify_game_started(game.uid)

        # Send turn notification
        GameNotifications.notify_turn_changed(
            game_id=game.uid,
            player_id=game_state.current_player_uid
        )

        return Response({
            "success": True,
            "message": "Game started successfully",
            "game_state": game_state.serialize(for_player_id=player.uid)
        })
