from .models import Game, Player, Card, Deck, GameCard, GameRuleSet, GameAction, GamePlayer, PlayerGroup, PlayerGroupInvitation
import uuid
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class PlayerGroupService:
    """Service for managing player groups"""

    @staticmethod
    def create_group(owner_id, name, description="", is_public=False):
        """Create a new player group"""
        owner = Player.nodes.get(user_id=owner_id)

        # Create the group
        group = PlayerGroup(
            group_id=str(uuid.uuid4()),
            name=name,
            description=description,
            is_public=is_public,
            created_at=datetime.now(),
            updated_at=datetime.now()
        ).save()

        # Connect the owner
        group.owner.connect(owner)
        group.members.connect(owner)
        owner.owned_groups.connect(group)
        owner.member_of_groups.connect(group)

        return group

    @staticmethod
    def invite_to_group(group_id, inviter_id, invitee_id):
        """Invite a player to join a group"""
        group = PlayerGroup.nodes.get(group_id=group_id)
        inviter = Player.nodes.get(user_id=inviter_id)
        invitee = Player.nodes.get(user_id=invitee_id)

        # Check if inviter is owner or member
        if not (group.owner.is_connected(inviter) or group.members.is_connected(inviter)):
            raise ValueError("Only group members can invite others")

        # Check if invitee is already a member
        if group.members.is_connected(invitee):
            raise ValueError("Player is already a member of this group")

        # Check for existing invitation
        existing_invitations = PlayerGroupInvitation.nodes.filter(
            status='pending'
        )

        for inv in existing_invitations:
            if (inv.group.get().group_id == group_id and
                inv.invitee.get().user_id == invitee_id):
                raise ValueError("Player already has a pending invitation to this group")

        # Create the invitation
        invitation = PlayerGroupInvitation(
            invitation_id=str(uuid.uuid4()),
            created_at=datetime.now(),
            status='pending'
        ).save()

        # Connect relationships
        invitation.group.connect(group)
        invitation.inviter.connect(inviter)
        invitation.invitee.connect(invitee)

        # Send notification
        PlayerGroupService.send_group_invitation_notification(group, inviter, invitee, invitation)

        return invitation

    @staticmethod
    def respond_to_group_invitation(invitation_id, response):
        """Accept or decline a group invitation"""
        invitation = PlayerGroupInvitation.nodes.get(invitation_id=invitation_id)

        if invitation.status != 'pending':
            raise ValueError("Invitation has already been processed")

        if response not in ['accepted', 'declined']:
            raise ValueError("Invalid response")

        # Update invitation status
        invitation.status = response
        invitation.save()

        group = invitation.group.get()
        invitee = invitation.invitee.get()

        # If accepted, add player to group
        if response == 'accepted':
            group.members.connect(invitee)
            invitee.member_of_groups.connect(group)

        # Send notification
        PlayerGroupService.send_group_invitation_response_notification(group, invitee, response)

        return invitation

    @staticmethod
    def get_player_groups(player_id):
        """Get all groups a player is a member of"""
        player = Player.nodes.get(user_id=player_id)
        return list(player.member_of_groups.all())

    @staticmethod
    def get_group_members(group_id):
        """Get all members of a group"""
        group = PlayerGroup.nodes.get(group_id=group_id)
        return list(group.members.all())

    @staticmethod
    def remove_from_group(group_id, owner_id, player_id):
        """Remove a player from a group"""
        group = PlayerGroup.nodes.get(group_id=group_id)
        owner = Player.nodes.get(user_id=owner_id)
        player = Player.nodes.get(user_id=player_id)

        # Check if remover is owner
        if not group.owner.is_connected(owner):
            raise ValueError("Only the group owner can remove members")

        # Check if player is a member
        if not group.members.is_connected(player):
            raise ValueError("Player is not a member of this group")

        # Cannot remove the owner
        if group.owner.is_connected(player):
            raise ValueError("Cannot remove the group owner")

        # Remove player from group
        group.members.disconnect(player)
        player.member_of_groups.disconnect(group)

        # Send notification
        PlayerGroupService.send_group_member_removed_notification(group, player)

        return group

    @staticmethod
    def leave_group(group_id, player_id):
        """Leave a group"""
        group = PlayerGroup.nodes.get(group_id=group_id)
        player = Player.nodes.get(user_id=player_id)

        # Check if player is a member
        if not group.members.is_connected(player):
            raise ValueError("Player is not a member of this group")

        # Cannot leave if player is the owner
        if group.owner.is_connected(player):
            raise ValueError("The owner cannot leave the group. Transfer ownership first or delete the group.")

        # Remove player from group
        group.members.disconnect(player)
        player.member_of_groups.disconnect(group)

        # Send notification
        PlayerGroupService.send_group_member_left_notification(group, player)

        return group

    @staticmethod
    def delete_group(group_id, owner_id):
        """Delete a group"""
        group = PlayerGroup.nodes.get(group_id=group_id)
        owner = Player.nodes.get(user_id=owner_id)

        # Check if user is owner
        if not group.owner.is_connected(owner):
            raise ValueError("Only the group owner can delete the group")

        # Get all members for notifications
        members = list(group.members.all())

        # Delete the group
        # In a real implementation, you might want to archive instead of delete
        group.delete()

        # Send notifications to all members
        for member in members:
            PlayerGroupService.send_group_deleted_notification(group_id, member)

        return True

    @staticmethod
    def invite_group_to_game(game_id, group_id, inviter_id):
        """Invite an entire group to a game"""
        game = Game.nodes.get(game_id=game_id)
        group = PlayerGroup.nodes.get(group_id=group_id)
        inviter = Player.nodes.get(user_id=inviter_id)

        # Check if inviter is the game creator
        if not game.creator.is_connected(inviter):
            raise ValueError("Only the game creator can invite groups")

        # Check if game is in created or waiting status
        if game.status not in ['created', 'waiting']:
            raise ValueError("Cannot invite players to a game that is not in created or waiting status")

        # Connect the group to the game
        game.invited_groups.connect(group)

        # Get all group members
        members = list(group.members.all())

        # Invite each member individually
        invited_players = []
        for member in members:
            # Skip the inviter if they're in the group
            if member.user_id == inviter_id:
                continue

            # Skip players already in the game
            if game.players.is_connected(member):
                continue

            try:
                # Use the existing invite_player method
                game_player = GameService.invite_player(
                    game_id=game_id,
                    player_id=member.user_id,
                    inviter_id=inviter_id
                )
                invited_players.append(member)
            except Exception as e:
                print(f"Error inviting player {member.username}: {str(e)}")

        # Send group invitation notification
        PlayerGroupService.send_group_game_invitation_notification(game, group, inviter, invited_players)

        return invited_players

    # WebSocket notification methods
    @staticmethod
    def send_group_invitation_notification(group, inviter, invitee, invitation):
        """Send a notification to a player that they have been invited to a group"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            invitation_data = {
                'invitation_id': invitation.invitation_id,
                'group_id': group.group_id,
                'group_name': group.name,
                'inviter_id': inviter.user_id,
                'inviter_username': inviter.username,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the invitee's personal channel
            async_to_sync(channel_layer.group_send)(
                f'user_{invitee.user_id}',
                {
                    'type': 'group_invitation',
                    'data': invitation_data
                }
            )
        except Exception as e:
            print(f"Error sending group invitation notification: {str(e)}")

    @staticmethod
    def send_group_invitation_response_notification(group, player, response):
        """Send a notification that a player has responded to a group invitation"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the response data
            response_data = {
                'group_id': group.group_id,
                'group_name': group.name,
                'user_id': player.user_id,
                'username': player.username,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the group owner's personal channel
            owner = group.owner.get()
            async_to_sync(channel_layer.group_send)(
                f'user_{owner.user_id}',
                {
                    'type': 'group_invitation_response',
                    'data': response_data
                }
            )

            # If accepted, notify all group members
            if response == 'accepted':
                for member in group.members.all():
                    if member.user_id != player.user_id and member.user_id != owner.user_id:
                        async_to_sync(channel_layer.group_send)(
                            f'user_{member.user_id}',
                            {
                                'type': 'group_member_joined',
                                'data': {
                                    'group_id': group.group_id,
                                    'group_name': group.name,
                                    'user_id': player.user_id,
                                    'username': player.username,
                                    'timestamp': datetime.now().isoformat()
                                }
                            }
                        )
        except Exception as e:
            print(f"Error sending group invitation response notification: {str(e)}")

    @staticmethod
    def send_group_member_removed_notification(group, player):
        """Send a notification that a player has been removed from a group"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            notification_data = {
                'group_id': group.group_id,
                'group_name': group.name,
                'user_id': player.user_id,
                'username': player.username,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the removed player
            async_to_sync(channel_layer.group_send)(
                f'user_{player.user_id}',
                {
                    'type': 'group_removed_from',
                    'data': notification_data
                }
            )

            # Notify all remaining group members
            for member in group.members.all():
                if member.user_id != player.user_id:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member.user_id}',
                        {
                            'type': 'group_member_removed',
                            'data': notification_data
                        }
                    )
        except Exception as e:
            print(f"Error sending group member removed notification: {str(e)}")

    @staticmethod
    def send_group_member_left_notification(group, player):
        """Send a notification that a player has left a group"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            notification_data = {
                'group_id': group.group_id,
                'group_name': group.name,
                'user_id': player.user_id,
                'username': player.username,
                'timestamp': datetime.now().isoformat()
            }

            # Notify all remaining group members
            for member in group.members.all():
                if member.user_id != player.user_id:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member.user_id}',
                        {
                            'type': 'group_member_left',
                            'data': notification_data
                        }
                    )
        except Exception as e:
            print(f"Error sending group member left notification: {str(e)}")

    @staticmethod
    def send_group_deleted_notification(group_id, player):
        """Send a notification that a group has been deleted"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            notification_data = {
                'group_id': group_id,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the player
            async_to_sync(channel_layer.group_send)(
                f'user_{player.user_id}',
                {
                    'type': 'group_deleted',
                    'data': notification_data
                }
            )
        except Exception as e:
            print(f"Error sending group deleted notification: {str(e)}")

    @staticmethod
    def send_group_game_invitation_notification(game, group, inviter, invited_players):
        """Send a notification that a group has been invited to a game"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            notification_data = {
                'game_id': game.game_id,
                'game_type': game.game_type,
                'group_id': group.group_id,
                'group_name': group.name,
                'inviter_id': inviter.user_id,
                'inviter_username': inviter.username,
                'invited_count': len(invited_players),
                'timestamp': datetime.now().isoformat()
            }

            # Send to all group members
            for member in group.members.all():
                # Skip the inviter
                if member.user_id == inviter.user_id:
                    continue

                async_to_sync(channel_layer.group_send)(
                    f'user_{member.user_id}',
                    {
                        'type': 'group_game_invitation',
                        'data': notification_data
                    }
                )
        except Exception as e:
            print(f"Error sending group game invitation notification: {str(e)}")

class GameService:
    """Service for handling game logic and operations"""

    @staticmethod
    def create_game(creator_id, game_type="standard", max_players=2, time_limit=30, use_ai=False, rule_version="1.0"):
        """Create a new game with the specified parameters"""
        # Get the creator player
        creator = Player.nodes.get(user_id=creator_id)

        # Get the rule set
        rule_set = GameRuleSet.nodes.get(version=rule_version)

        # Create the game
        game = Game(
            game_id=str(uuid.uuid4()),
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
            player_id=str(uuid.uuid4()),
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
    def invite_player(game_id, player_id, inviter_id):
        """Invite a player to join a game"""
        game = Game.nodes.get(game_id=game_id)
        player = Player.nodes.get(user_id=player_id)
        inviter = Player.nodes.get(user_id=inviter_id)

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
            player_id=str(uuid.uuid4()),
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
    def add_ai_player(game_id, creator_id, difficulty="medium"):
        """Add an AI player to a game"""
        game = Game.nodes.get(game_id=game_id)
        creator = Player.nodes.get(user_id=creator_id)

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
            player_id=str(uuid.uuid4()),
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
    def accept_invitation(game_id, player_id):
        """Accept an invitation to join a game"""
        game = Game.nodes.get(game_id=game_id)
        player = Player.nodes.get(user_id=player_id)

        # Find the GamePlayer for this player and game
        game_players = player.game_players.all()
        game_player = None

        for gp in game_players:
            if gp.game.get().game_id == game_id:
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
    def decline_invitation(game_id, player_id):
        """Decline an invitation to join a game"""
        game = Game.nodes.get(game_id=game_id)
        player = Player.nodes.get(user_id=player_id)

        # Find the GamePlayer for this player and game
        game_players = player.game_players.all()
        game_player = None

        for gp in game_players:
            if gp.game.get().game_id == game_id:
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
    def search_players(query, current_user_id):
        """Search for players by username or display name"""
        # Exclude the current user from results
        results = Player.nodes.filter(
            username__icontains=query
        ).exclude(
            user_id=current_user_id
        )

        return list(results)

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

        # Create a GamePlayer for the player
        game_player = GamePlayer(
            player_id=str(uuid.uuid4()),
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

        # Send notification to all players in the game
        GameService.send_game_started_notification(game)

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

    # WebSocket notification methods
    @staticmethod
    def send_invitation_notification(game, player, inviter):
        """Send a notification to a player that they have been invited to a game"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            invitation_data = {
                'game_id': game.game_id,
                'game_type': game.game_type,
                'max_players': game.max_players,
                'time_limit': game.time_limit,
                'inviter_id': inviter.user_id,
                'inviter_username': inviter.username,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the player's personal channel
            async_to_sync(channel_layer.group_send)(
                f'user_{player.user_id}',
                {
                    'type': 'game_invitation',
                    'data': invitation_data
                }
            )

            # Also send to the game channel to notify other players
            player_data = {
                'user_id': player.user_id,
                'username': player.username,
                'display_name': player.display_name,
                'status': 'invited',
                'timestamp': datetime.now().isoformat()
            }

            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_id}',
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
                'user_id': player.user_id,
                'username': player.username,
                'display_name': player.display_name,
                'response': response,
                'game_id': game.game_id,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the game channel
            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_id}',
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
                f'user_{creator.user_id}',
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
                    'game_id': game.game_id,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Human player
                player_data = {
                    'user_id': player.user_id,
                    'username': player.username,
                    'display_name': player.display_name,
                    'status': 'accepted',
                    'game_id': game.game_id,
                    'timestamp': datetime.now().isoformat()
                }

            # Send to the game channel
            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_id}',
                {
                    'type': 'player_joined',
                    'data': player_data
                }
            )

            # Also update all players individually to ensure they receive the update
            # even if they're not actively listening to this game channel
            for p in game.players.all():
                if not isinstance(player, dict) and p.user_id == player.user_id:
                    continue  # Skip sending to the player who just joined

                async_to_sync(channel_layer.group_send)(
                    f'user_{p.user_id}',
                    {
                        'type': 'game_update',
                        'data': {
                            'update_type': 'player_joined',
                            'game_id': game.game_id,
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
                'game_id': game.game_id,
                'started_at': game.started_at.isoformat() if game.started_at else None,
                'current_player': game.current_player.get().user_id if game.current_player.all() else None,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the game channel
            async_to_sync(channel_layer.group_send)(
                f'game_{game.game_id}',
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
                    game.current_player.get().user_id == player.user_id
                )

                async_to_sync(channel_layer.group_send)(
                    f'user_{player.user_id}',
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
