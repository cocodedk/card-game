from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import GameService
from .models import Game, Player, Card, Deck
from django.contrib.auth.models import User
from authentication.models import UserProfile

class GameViewSet(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def list(self, request):
        """List all games the user is participating in"""
        # Get the user's player node
        try:
            player = Player.nodes.get(user_id=request.user.id)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get all games the player is participating in
        games = player.games.all()

        # Format the response
        game_data = []
        for game in games:
            players = [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "display_name": p.display_name
                }
                for p in game.players.all()
            ]

            current_player = None
            if game.current_player.all():
                current_player = game.current_player.get().user_id

            winner = None
            if game.winner.all():
                winner = game.winner.get().user_id

            game_data.append({
                "game_id": game.game_id,
                "status": game.status,
                "current_turn": game.current_turn,
                "created_at": game.created_at.isoformat() if game.created_at else None,
                "started_at": game.started_at.isoformat() if game.started_at else None,
                "ended_at": game.ended_at.isoformat() if game.ended_at else None,
                "players": players,
                "current_player": current_player,
                "winner": winner,
                "rule_version": game.rule_version
            })

        return Response(game_data)

    def create(self, request):
        """Create a new game"""
        try:
            # Create the game
            game = GameService.create_game(
                creator_id=request.user.id,
                rule_version=request.data.get('rule_version', '1.0')
            )

            return Response({
                "game_id": game.game_id,
                "status": game.status,
                "message": "Game created successfully"
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Get details of a specific game"""
        try:
            game = Game.nodes.get(game_id=pk)

            # Check if the user is a participant
            player = Player.nodes.get(user_id=request.user.id)
            if not game.players.is_connected(player):
                return Response({"error": "You are not a participant in this game"},
                               status=status.HTTP_403_FORBIDDEN)

            # Format the response
            players = [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "display_name": p.display_name
                }
                for p in game.players.all()
            ]

            current_player = None
            if game.current_player.all():
                current_player = game.current_player.get().user_id

            winner = None
            if game.winner.all():
                winner = game.winner.get().user_id

            game_data = {
                "game_id": game.game_id,
                "status": game.status,
                "current_turn": game.current_turn,
                "created_at": game.created_at.isoformat() if game.created_at else None,
                "started_at": game.started_at.isoformat() if game.started_at else None,
                "ended_at": game.ended_at.isoformat() if game.ended_at else None,
                "players": players,
                "current_player": current_player,
                "winner": winner,
                "rule_version": game.rule_version
            }

            return Response(game_data)
        except Game.DoesNotExist:
            return Response({"error": "Game not found"}, status=status.HTTP_404_NOT_FOUND)
        except Player.DoesNotExist:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join an existing game"""
        try:
            game = GameService.join_game(
                game_id=pk,
                player_id=request.user.id
            )

            return Response({
                "game_id": game.game_id,
                "status": game.status,
                "message": "Joined game successfully"
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a game"""
        try:
            game = Game.nodes.get(game_id=pk)
            player = Player.nodes.get(user_id=request.user.id)

            # Check if the user is the creator (first player)
            players = list(game.players.all())
            if not players or players[0].user_id != request.user.id:
                return Response({"error": "Only the game creator can start the game"},
                               status=status.HTTP_403_FORBIDDEN)

            game = GameService.start_game(pk)

            return Response({
                "game_id": game.game_id,
                "status": game.status,
                "message": "Game started successfully"
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def play_card(self, request, pk=None):
        """Play a card in the game"""
        try:
            card_instance_id = request.data.get('card_instance_id')
            target_position = request.data.get('target_position')

            if not card_instance_id or target_position is None:
                return Response({"error": "Missing required parameters"},
                               status=status.HTTP_400_BAD_REQUEST)

            card_instance = GameService.play_card(
                game_id=pk,
                player_id=request.user.id,
                card_instance_id=card_instance_id,
                target_position=target_position
            )

            return Response({
                "message": "Card played successfully",
                "card_instance_id": card_instance.instance_id,
                "location": card_instance.location,
                "position": card_instance.position
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def end_turn(self, request, pk=None):
        """End the current player's turn"""
        try:
            game = GameService.end_turn(
                game_id=pk,
                player_id=request.user.id
            )

            return Response({
                "message": "Turn ended successfully",
                "current_turn": game.current_turn,
                "current_player": game.current_player.get().user_id
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
