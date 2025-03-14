import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Game, Player, GamePlayer, PlayerGroup

# Don't import User directly at module level
# from django.contrib.auth.models import User

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.game_id = self.scope['url_route']['kwargs'].get('game_id')
        self.group_id = self.scope['url_route']['kwargs'].get('group_id')
        self.groups = []  # Track all groups this connection belongs to

        # Always connect to the user's personal channel
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        self.groups.append(self.user_group_name)

        # If connecting to a specific game, join that game's group too
        if self.game_id:
            self.game_group_name = f'game_{self.game_id}'
            await self.channel_layer.group_add(
                self.game_group_name,
                self.channel_name
            )
            self.groups.append(self.game_group_name)

            # Send initial game state
            game_data = await self.get_game_data(self.game_id)
            if game_data:
                await self.send(text_data=json.dumps({
                    'type': 'game_state',
                    'data': game_data
                }))
        # If connecting to a specific player group, join that group's channel
        elif self.group_id:
            self.player_group_name = f'player_group_{self.group_id}'
            await self.channel_layer.group_add(
                self.player_group_name,
                self.channel_name
            )
            self.groups.append(self.player_group_name)

            # Send initial group state
            group_data = await self.get_player_group_data(self.group_id)
            if group_data:
                await self.send(text_data=json.dumps({
                    'type': 'player_group_state',
                    'data': group_data
                }))
        else:
            # If not connecting to a specific game or group, get all active games and groups for the user
            active_games = await self.get_user_active_games()
            player_groups = await self.get_user_groups()

            # Send combined data
            await self.send(text_data=json.dumps({
                'type': 'user_state',
                'data': {
                    'active_games': active_games,
                    'player_groups': player_groups
                }
            }))

        await self.accept()

    async def disconnect(self, close_code):
        # Leave all groups
        for group_name in self.groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong'
            }))
        elif message_type == 'subscribe_game':
            # Allow dynamic subscription to additional games
            game_id = text_data_json.get('game_id')
            if game_id and f'game_{game_id}' not in self.groups:
                game_group_name = f'game_{game_id}'
                await self.channel_layer.group_add(
                    game_group_name,
                    self.channel_name
                )
                self.groups.append(game_group_name)

                # Send initial game state for the newly subscribed game
                game_data = await self.get_game_data(game_id)
                if game_data:
                    await self.send(text_data=json.dumps({
                        'type': 'game_state',
                        'data': game_data
                    }))
        elif message_type == 'unsubscribe_game':
            # Allow unsubscribing from games to reduce connection load
            game_id = text_data_json.get('game_id')
            game_group_name = f'game_{game_id}'
            if game_group_name in self.groups:
                await self.channel_layer.group_discard(
                    game_group_name,
                    self.channel_name
                )
                self.groups.remove(game_group_name)
        elif message_type == 'subscribe_player_group':
            # Allow dynamic subscription to player groups
            group_id = text_data_json.get('group_id')
            if group_id and f'player_group_{group_id}' not in self.groups:
                player_group_name = f'player_group_{group_id}'
                await self.channel_layer.group_add(
                    player_group_name,
                    self.channel_name
                )
                self.groups.append(player_group_name)

                # Send initial group state
                group_data = await self.get_player_group_data(group_id)
                if group_data:
                    await self.send(text_data=json.dumps({
                        'type': 'player_group_state',
                        'data': group_data
                    }))
        elif message_type == 'unsubscribe_player_group':
            # Allow unsubscribing from player groups
            group_id = text_data_json.get('group_id')
            player_group_name = f'player_group_{group_id}'
            if player_group_name in self.groups:
                await self.channel_layer.group_discard(
                    player_group_name,
                    self.channel_name
                )
                self.groups.remove(player_group_name)

    # Receive message from room group
    async def game_update(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'data': event['data']
        }))

    async def game_invitation(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_invitation',
            'data': event['data']
        }))

    async def invitation_response(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'invitation_response',
            'data': event['data']
        }))

    async def player_joined(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'data': event['data']
        }))

    async def player_left(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'data': event['data']
        }))

    async def game_started(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'data': event['data']
        }))

    async def batch_update(self, event):
        """Handle batched updates to reduce message overhead"""
        # Send all updates in a single message
        await self.send(text_data=json.dumps({
            'type': 'batch_update',
            'updates': event['updates']
        }))

    # Group-related message handlers
    async def group_invitation(self, event):
        """Handle group invitation notifications"""
        await self.send(text_data=json.dumps({
            'type': 'group_invitation',
            'data': event['data']
        }))

    async def group_invitation_response(self, event):
        """Handle group invitation response notifications"""
        await self.send(text_data=json.dumps({
            'type': 'group_invitation_response',
            'data': event['data']
        }))

    async def group_member_joined(self, event):
        """Handle notifications when a new member joins a group"""
        await self.send(text_data=json.dumps({
            'type': 'group_member_joined',
            'data': event['data']
        }))

    async def group_member_removed(self, event):
        """Handle notifications when a member is removed from a group"""
        await self.send(text_data=json.dumps({
            'type': 'group_member_removed',
            'data': event['data']
        }))

    async def group_member_left(self, event):
        """Handle notifications when a member leaves a group"""
        await self.send(text_data=json.dumps({
            'type': 'group_member_left',
            'data': event['data']
        }))

    async def group_removed_from(self, event):
        """Handle notifications when the user is removed from a group"""
        await self.send(text_data=json.dumps({
            'type': 'group_removed_from',
            'data': event['data']
        }))

    async def group_deleted(self, event):
        """Handle notifications when a group is deleted"""
        await self.send(text_data=json.dumps({
            'type': 'group_deleted',
            'data': event['data']
        }))

    async def group_game_invitation(self, event):
        """Handle notifications when a group is invited to a game"""
        await self.send(text_data=json.dumps({
            'type': 'group_game_invitation',
            'data': event['data']
        }))

    @database_sync_to_async
    def get_user_active_games(self):
        """Get all active games for the current user"""
        try:
            player = Player.nodes.get(user_id=self.user.id)
            games = player.games.filter(status__in=['waiting', 'in_progress'])

            return [
                {
                    "game_id": game.game_id,
                    "status": game.status,
                    "game_type": game.game_type
                }
                for game in games
            ]
        except Exception as e:
            print(f"Error getting user active games: {str(e)}")
            return []

    @database_sync_to_async
    def get_user_groups(self):
        """Get all groups the user is a member of"""
        try:
            player = Player.nodes.get(user_id=self.user.id)
            groups = player.member_of_groups.all()

            return [
                {
                    "group_id": group.group_id,
                    "name": group.name,
                    "is_owner": group.owner.is_connected(player),
                    "member_count": len(list(group.members.all()))
                }
                for group in groups
            ]
        except Exception as e:
            print(f"Error getting user groups: {str(e)}")
            return []

    @database_sync_to_async
    def get_player_group_data(self, group_id):
        """Get detailed data for a player group"""
        try:
            group = PlayerGroup.nodes.get(group_id=group_id)
            player = Player.nodes.get(user_id=self.user.id)

            # Check if user is a member
            if not group.members.is_connected(player):
                return None

            # Get all members
            members = []
            for member in group.members.all():
                members.append({
                    "user_id": member.user_id,
                    "username": member.username,
                    "display_name": member.display_name,
                    "is_owner": group.owner.is_connected(member)
                })

            # Get active games the group is participating in
            active_games = []
            for game in group.games.filter(status__in=['waiting', 'in_progress']):
                active_games.append({
                    "game_id": game.game_id,
                    "game_type": game.game_type,
                    "status": game.status
                })

            return {
                "group_id": group.group_id,
                "name": group.name,
                "description": group.description,
                "is_public": group.is_public,
                "created_at": group.created_at.isoformat() if group.created_at else None,
                "is_owner": group.owner.is_connected(player),
                "members": members,
                "active_games": active_games
            }
        except Exception as e:
            print(f"Error getting player group data: {str(e)}")
            return None

    @database_sync_to_async
    def get_game_data(self, game_id):
        try:
            game = Game.nodes.get(game_id=game_id)

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

            # Get invited groups
            invited_groups = []
            for group in game.invited_groups.all():
                invited_groups.append({
                    "group_id": group.group_id,
                    "name": group.name
                })

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
                "rule_version": game.rule_version,
                "is_tournament": game.is_tournament,
                "tournament_round": game.tournament_round,
                "invited_groups": invited_groups
            }

            return game_data
        except Game.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting game data: {str(e)}")
            return None

    # Use lazy imports for Django models when needed
    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
