from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..services import GameService
from ..models import Game, Player

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

            creator = None
            if game.creator.all():
                creator = game.creator.get().user_id

            game_data.append({
                "game_id": game.game_id,
                "game_type": game.game_type,
                "max_players": game.max_players,
                "time_limit": game.time_limit,
                "use_ai": game.use_ai,
                "status": game.status,
                "current_turn": game.current_turn,
                "created_at": game.created_at.isoformat() if game.created_at else None,
                "started_at": game.started_at.isoformat() if game.started_at else None,
                "ended_at": game.ended_at.isoformat() if game.ended_at else None,
                "completed_at": game.completed_at.isoformat() if game.completed_at else None,
                "players": players,
                "creator": creator,
                "current_player": current_player,
                "winner": winner,
                "rule_version": game.rule_version
            })

        return Response(game_data)

    def create(self, request):
        """Create a new game"""
        try:
            # Extract game configuration parameters
            game_type = request.data.get('game_type', 'standard')
            max_players = int(request.data.get('max_players', 2))
            time_limit = int(request.data.get('time_limit', 30))
            use_ai = request.data.get('use_ai', False)
            rule_version = request.data.get('rule_version', '1.0')

            # Validate parameters
            if game_type not in ['standard', 'quick', 'tournament']:
                return Response({"error": "Invalid game type"}, status=status.HTTP_400_BAD_REQUEST)

            if max_players < 2 or max_players > 8:
                return Response({"error": "Max players must be between 2 and 8"}, status=status.HTTP_400_BAD_REQUEST)

            if time_limit < 5 or time_limit > 120:
                return Response({"error": "Time limit must be between 5 and 120 minutes"}, status=status.HTTP_400_BAD_REQUEST)

            # Create the game
            game = GameService.create_game(
                creator_id=request.user.id,
                game_type=game_type,
                max_players=max_players,
                time_limit=time_limit,
                use_ai=use_ai,
                rule_version=rule_version
            )

            return Response({
                "game_id": game.game_id,
                "game_type": game.game_type,
                "max_players": game.max_players,
                "time_limit": game.time_limit,
                "use_ai": game.use_ai,
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
            players = []
            for p in game.players.all():
                # Find the GamePlayer for this player
                game_player = None
                for gp in p.game_players.all():
                    try:
                        if gp.game.get().game_id == game.game_id:
                            game_player = gp
                            break
                    except:
                        continue

                player_data = {
                    "user_id": p.user_id,
                    "username": p.username,
                    "display_name": p.display_name,
                    "status": game_player.status if game_player else "unknown"
                }
                players.append(player_data)

            # Add AI players
            for gp in game.game_players.all():
                if gp.is_ai:
                    ai_player = {
                        "is_ai": True,
                        "ai_difficulty": gp.ai_difficulty,
                        "status": gp.status
                    }
                    players.append(ai_player)

            current_player = None
            if game.current_player.all():
                current_player = game.current_player.get().user_id

            winner = None
            if game.winner.all():
                winner = game.winner.get().user_id

            creator = None
            if game.creator.all():
                creator = game.creator.get().user_id

            game_data = {
                "game_id": game.game_id,
                "game_type": game.game_type,
                "max_players": game.max_players,
                "time_limit": game.time_limit,
                "use_ai": game.use_ai,
                "status": game.status,
                "current_turn": game.current_turn,
                "created_at": game.created_at.isoformat() if game.created_at else None,
                "started_at": game.started_at.isoformat() if game.started_at else None,
                "ended_at": game.ended_at.isoformat() if game.ended_at else None,
                "completed_at": game.completed_at.isoformat() if game.completed_at else None,
                "players": players,
                "creator": creator,
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
    def invite(self, request, pk=None):
        """Invite a player to join a game"""
        try:
            player_id = request.data.get('player_id')

            if not player_id:
                return Response({"error": "Player ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            game_player = GameService.invite_player(
                game_id=pk,
                player_id=player_id,
                inviter_id=request.user.id
            )

            return Response({
                "message": "Player invited successfully",
                "player_id": player_id,
                "status": game_player.status
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_ai(self, request, pk=None):
        """Add an AI player to a game"""
        try:
            difficulty = request.data.get('difficulty', 'medium')

            if difficulty not in ['easy', 'medium', 'hard', 'expert']:
                return Response({"error": "Invalid difficulty level"}, status=status.HTTP_400_BAD_REQUEST)

            game_player = GameService.add_ai_player(
                game_id=pk,
                creator_id=request.user.id,
                difficulty=difficulty
            )

            return Response({
                "message": "AI player added successfully",
                "difficulty": game_player.ai_difficulty,
                "status": game_player.status
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept an invitation to join a game"""
        try:
            game_player = GameService.accept_invitation(
                game_id=pk,
                player_id=request.user.id
            )

            return Response({
                "message": "Invitation accepted",
                "status": game_player.status
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline an invitation to join a game"""
        try:
            game_player = GameService.decline_invitation(
                game_id=pk,
                player_id=request.user.id
            )

            return Response({
                "message": "Invitation declined",
                "status": game_player.status
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def search_players(self, request):
        """Search for players by username"""
        try:
            query = request.query_params.get('query', '')

            if not query:
                return Response({"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)

            players = GameService.search_players(
                query=query,
                current_user_id=request.user.id
            )

            player_data = [
                {
                    "user_id": p.user_id,
                    "username": p.username,
                    "display_name": p.display_name
                }
                for p in players
            ]

            return Response(player_data)
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

            # Check if the user is the creator
            if not game.creator.is_connected(player):
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
