from backend.game.models import Game, Player, GameCard, GameRuleSet, GameAction, GamePlayer
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class GameService:
    """Service for handling game logic and operations"""

    @staticmethod
    def create_game(creator_uid, game_type="standard", max_players=2, time_limit=30, use_ai=False, rule_version="1.0"):
        """Create a new game with the specified parameters"""
        # Get the creator player
        creator = Player.nodes.get(uid=creator_uid)

        # Get the rule set
        rule_set = GameRuleSet.nodes.get(version=rule_version)

        # Create the game
        game = Game(
            game_type=game_type,
            max_players=max_players,
            time_limit=time_limit,
            use_ai=use_ai,
            status='created',
            rule_version=rule_version,
            created_at=datetime.now()
        ).save()

        # Connect the creator to the game
        game.players.connect(creator)
        game.creator.connect(creator)

        # Connect the rule set to the game
        game.rule_set.connect(rule_set)

        # Create a GamePlayer for the creator
        game_player = GamePlayer(
            is_ai=False,
            status='accepted',
            joined_at=datetime.now()
        ).save()

        # Connect the GamePlayer to the Game and Player
        game.game_players.connect(game_player)
        creator.game_players.connect(game_player)

        # Update game status to waiting
        game.status = 'waiting'
        game.save()

        return game

    @staticmethod
    def invite_player(game_uid, player_uid, inviter_uid):
        """Invite a player to join a game"""
        game = Game.nodes.get(uid=game_uid)
        player = Player.nodes.get(uid=player_uid)
        inviter = Player.nodes.get(uid=inviter_uid)

        # Check if game is in created or waiting status
        if game.status not in ['created', 'waiting']:
            raise ValueError("Cannot invite players to a game that is not in created or waiting status")

        # Check if inviter is the creator
        if not game.creator.is_connected(inviter):
            raise ValueError("Only the game creator can invite players")

        # Check if player is already in the game
        if game.players.is_connected(player):
            raise ValueError("Player is already in the game")

        # Check if max players reached
        current_players = len(list(game.players.all()))
        if current_players >= game.max_players:
            raise ValueError(f"Game already has maximum number of players ({game.max_players})")

        # Create a GamePlayer for the invited player
        game_player = GamePlayer(
            is_ai=False,
            status='invited',
            joined_at=datetime.now()
        ).save()

        # Connect the GamePlayer to the Game and Player
        game.game_players.connect(game_player)
        player.game_players.connect(game_player)

        # Send notification to the invited player
        GameService.send_invitation_notification(game, player, inviter)

        return game_player

    @staticmethod
    def add_ai_player(game_uid, creator_uid, difficulty="medium"):
        """Add an AI player to a game"""
        game = Game.nodes.get(uid=game_uid)
        creator = Player.nodes.get(uid=creator_uid)

        # Check if game is in created or waiting status
        if game.status not in ['created', 'waiting']:
            raise ValueError("Cannot add AI players to a game that is not in created or waiting status")

        # Check if creator is the game creator
        if not game.creator.is_connected(creator):
            raise ValueError("Only the game creator can add AI players")

        # Check if max players reached
        current_players = len(list(game.players.all()))
        if current_players >= game.max_players:
            raise ValueError(f"Game already has maximum number of players ({game.max_players})")

        # Check if game allows AI
        if not game.use_ai:
            raise ValueError("This game does not allow AI players")

        # Create a GamePlayer for the AI player
        game_player = GamePlayer(
            is_ai=True,
            ai_difficulty=difficulty,
            status='accepted',
            joined_at=datetime.now()
        ).save()

        # Connect the GamePlayer to the Game
        game.game_players.connect(game_player)

        # Send notification to all players in the game
        GameService.send_player_joined_notification(game, {
            'is_ai': True,
            'ai_difficulty': difficulty
        })

        return game_player

    @staticmethod
    def accept_invitation(game_uid, player_uid):
        """Accept an invitation to join a game"""
        game = Game.nodes.get(uid=game_uid)
        player = Player.nodes.get(uid=player_uid)

        # Find the GamePlayer for this player and game
        game_players = player.game_players.all()
        game_player = None

        for gp in game_players:
            if gp.game.get().game_uid == game_uid:
                game_player = gp
                break

        if not game_player:
            raise ValueError("No invitation found for this player and game")

        if game_player.status != 'invited':
            raise ValueError("Invitation has already been processed")

        # Update the GamePlayer status
        game_player.status = 'accepted'
        game_player.save()

        # Connect the player to the game if not already connected
        if not game.players.is_connected(player):
            game.players.connect(player)

        # Send notification to all players in the game
        GameService.send_invitation_response_notification(game, player, 'accepted')

        return game_player

    @staticmethod
    def decline_invitation(game_uid, player_uid):
        """Decline an invitation to join a game"""
        game = Game.nodes.get(game_uid=game_uid)
        player = Player.nodes.get(user_uid=player_uid)

        # Find the GamePlayer for this player and game
        game_players = player.game_players.all()
        game_player = None

        for gp in game_players:
            if gp.game.get().game_uid == game_uid:
                game_player = gp
                break

        if not game_player:
            raise ValueError("No invitation found for this player and game")

        if game_player.status != 'invited':
            raise ValueError("Invitation has already been processed")

        # Update the GamePlayer status
        game_player.status = 'declined'
        game_player.save()

        # Send notification to all players in the game
        GameService.send_invitation_response_notification(game, player, 'declined')

        return game_player

    @staticmethod
    def search_players(query, current_user_uid):
        """Search for players by username or display name"""
        # Exclude the current user from results
        results = Player.nodes.filter(
            username__icontains=query
        ).exclude(
            user_uid=current_user_uid
        )

        return list(results)

    @staticmethod
    def join_game(game_uid, player_uid):
        """Add a player to an existing game"""
        game = Game.nodes.get(uid=game_uid)
        player = Player.nodes.get(uid=player_uid)

        # Check if game is in waiting status
        if game.status != 'waiting':
            raise ValueError("Cannot join a game that is not in waiting status")

        # Connect player to game
        game.players.connect(player)

        # Create a GamePlayer for the player
        game_player = GamePlayer(
            is_ai=False,
            status='accepted',
            joined_at=datetime.now()
        ).save()

        # Connect the GamePlayer to the Game and Player
        game.game_players.connect(game_player)
        player.game_players.connect(game_player)

        # Send notification to all players in the game
        GameService.send_player_joined_notification(game, player)

        return game

    @staticmethod
    def start_game(game_uid):
        """Start a game that is in waiting status"""
        game = Game.nodes.get(uid=game_uid)

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

        # Send notification to all players in the game
        GameService.send_game_started_notification(game)

        return game

    @staticmethod
    def play_card(game_uid, player_uid, card_instance_uid, target_position):
        """Play a card from a player's hand to the field"""
        game = Game.nodes.get(uid=game_uid)
        player = Player.nodes.get(uid=player_uid)
        card_instance = GameCard.nodes.get(uid=card_instance_uid)

        # Check if it's the player's turn
        current_player = game.current_player.get()
        if current_player.uid != player_uid:
            raise ValueError("It's not your turn")

        # Check if the card is in the player's hand
        if card_instance.location != 'hand' or card_instance.owner.get().uid != player_uid:
            raise ValueError("Card is not in your hand")

        # Move the card to the field
        card_instance.location = 'field'
        card_instance.position = target_position
        card_instance.save()

        # Record the action
        GameAction(
            action_type='play_card',
            action_data={
                'card_uid': card_instance.uid,
                'position': target_position
            }
        ).save().game.connect(game).player.connect(player).affected_cards.connect(card_instance)

        return card_instance

    @staticmethod
    def end_turn(game_uid, player_uid):
        """End the current player's turn and move to the next player"""
        game = Game.nodes.get(uid=game_uid)
        player = Player.nodes.get(uid=player_uid)

        # Check if it's the player's turn
        current_player = game.current_player.get()
        if current_player.uid != player_uid:
            raise ValueError("It's not your turn")

        # Get all players
        players = list(game.players.all())

        # Find the index of the current player
        current_index = next((i for i, p in enumerate(players) if p.uid == player_uid), None)

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
    def end_game(game_uid, winner_uid=None):
        """End a game and set the winner if provided"""
        game = Game.nodes.get(uid=game_uid)

        # Update game status
        game.status = 'completed'
        game.ended_at = datetime.now()
        game.save()

        # Set the winner if provided
        if winner_uid:
            winner = Player.nodes.get(uid=winner_uid)
            game.winner.connect(winner)

        return game

    # WebSocket notification methods
    @staticmethod
    def send_invitation_notification(game, player, inviter):
        """Send a notification to a player that they have been invited to a game"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            invitation_data = {
                'game_uid': game.game_uid,
                'game_type': game.game_type,
                'max_players': game.max_players,
                'time_limit': game.time_limit,
                'inviter_uid': inviter.uid,
                'inviter_username': inviter.username,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the player's personal channel
            async_to_sync(channel_layer.group_send)(
                f'user_{player.uid}',
                {
                    'type': 'game_invitation',
                    'data': invitation_data
                }
            )

            # Also send to the game channel to notify other players
            player_data = {
                'user_uid': player.uid,
                'username': player.username,
                'display_name': player.display_name,
                'status': 'invited',
                'timestamp': datetime.now().isoformat()
            }

            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_uid}',
                {
                    'type': 'player_joined',
                    'data': player_data
                }
            )
        except Exception as e:
            print(f"Error sending invitation notification: {str(e)}")

    @staticmethod
    def send_invitation_response_notification(game, player, response):
        """Send a notification to all players in a game that a player has responded to an invitation"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the response data
            response_data = {
                'user_uid': player.uid,
                'username': player.username,
                'display_name': player.display_name,
                'response': response,
                'game_uid': game.game_uid,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the game channel
            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_uid}',
                {
                    'type': 'invitation_response',
                    'data': response_data
                }
            )

            # Also send to the creator's personal channel
            creator = game.creator.get()

            # Add creator-specific data
            creator_data = response_data.copy()
            creator_data['is_creator_notification'] = True

            async_to_sync(channel_layer.group_send)(
                f'user_{creator.uid}',
                {
                    'type': 'invitation_response',
                    'data': creator_data
                }
            )
        except Exception as e:
            print(f"Error sending invitation response notification: {str(e)}")

    @staticmethod
    def send_player_joined_notification(game, player):
        """Send a notification to all players in a game that a player has joined"""
        try:
            channel_layer = get_channel_layer()

            # Prepare player data
            if isinstance(player, dict) and player.get('is_ai'):
                # AI player
                player_data = {
                    'is_ai': True,
                    'ai_difficulty': player.get('ai_difficulty', 'medium'),
                    'status': 'accepted',
                    'game_uid': game.game_uid,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Human player
                player_data = {
                    'user_uid': player.uid,
                    'username': player.username,
                    'display_name': player.display_name,
                    'status': 'accepted',
                    'game_uid': game.game_uid,
                    'timestamp': datetime.now().isoformat()
                }

            # Send to the game channel
            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_uid}',
                {
                    'type': 'player_joined',
                    'data': player_data
                }
            )

            # Also update all players individually to ensure they receive the update
            # even if they're not actively listening to this game channel
            for p in game.players.all():
                if not isinstance(player, dict) and p.uid == player.uid:
                    continue  # Skip sending to the player who just joined

                async_to_sync(channel_layer.group_send)(
                    f'user_{p.uid}',
                    {
                        'type': 'game_update',
                        'data': {
                            'update_type': 'player_joined',
                            'game_uid': game.game_uid,
                            'player': player_data
                        }
                    }
                )
        except Exception as e:
            print(f"Error sending player joined notification: {str(e)}")

    @staticmethod
    def send_game_started_notification(game):
        """Send a notification to all players in a game that the game has started"""
        try:
            channel_layer = get_channel_layer()

            # Prepare game started data
            game_data = {
                'game_uid': game.game_uid,
                'started_at': game.started_at.isoformat() if game.started_at else None,
                'current_player': game.current_player.get().uid if game.current_player.all() else None,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the game channel
            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_uid}',
                {
                    'type': 'game_started',
                    'data': game_data
                }
            )

            # Also send to each player's personal channel with player-specific data
            for player in game.players.all():
                # Add player-specific data
                player_data = game_data.copy()
                player_data['is_your_turn'] = (
                    game.current_player.all() and
                    game.current_player.get().uid == player.uid
                )

                async_to_sync(channel_layer.group_send)(
                    f'user_{player.uid}',
                    {
                        'type': 'game_started',
                        'data': player_data
                    }
                )
        except Exception as e:
            print(f"Error sending game started notification: {str(e)}")

    @staticmethod
    def batch_send_game_updates(updates):
        """
        Send multiple game updates in a batch to reduce channel layer overhead

        Args:
            updates: List of dicts with keys:
                - channel_name: The channel to send to
                - type: The message type
                - data: The message data
        """
        try:
            if not updates:
                return

            channel_layer = get_channel_layer()

            # Group updates by channel
            channel_updates = {}
            for update in updates:
                channel = update['channel_name']
                if channel not in channel_updates:
                    channel_updates[channel] = []
                channel_updates[channel].append({
                    'type': update['type'],
                    'data': update['data']
                })

            # Send batched updates to each channel
            for channel, messages in channel_updates.items():
                async_to_sync(channel_layer.group_send)(
                    channel,
                    {
                        'type': 'batch_update',
                        'updates': messages
                    }
                )
        except Exception as e:
            print(f"Error sending batch game updates: {str(e)}")
