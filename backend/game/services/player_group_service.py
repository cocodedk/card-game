from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from backend.game.models import Game, Player, PlayerGroup, PlayerGroupInvitation
from backend.game.services import GameService


class PlayerGroupService:
    """Service for managing player groups"""

    @staticmethod
    def create_group(owner_uid, name, description="", is_public=False):
        """Create a new player group"""
        owner = Player.nodes.get(uid=owner_uid)

        # Create the group
        group = PlayerGroup(
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
    def invite_to_group(group_uid, inviter_uid, invitee_uid):
        """Invite a player to join a group"""
        group = PlayerGroup.nodes.get(uid=group_uid)
        inviter = Player.nodes.get(uid=inviter_uid)
        invitee = Player.nodes.get(uid=invitee_uid)

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
            if (inv.group.get().uid == group_uid and
                inv.invitee.get().uid == invitee_uid):
                raise ValueError("Player already has a pending invitation to this group")

        # Create the invitation
        invitation = PlayerGroupInvitation(
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
    def respond_to_group_invitation(invitation_uid, response):
        """Accept or decline a group invitation"""
        invitation = PlayerGroupInvitation.nodes.get(uid=invitation_uid)

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
    def get_player_groups(player_uid):
        """Get all groups a player is a member of"""
        player = Player.nodes.get(uid=player_uid)
        return list(player.member_of_groups.all())

    @staticmethod
    def get_group_members(group_uid):
        """Get all members of a group"""
        group = PlayerGroup.nodes.get(uid=group_uid)
        return list(group.members.all())

    @staticmethod
    def remove_from_group(group_uid, owner_uid, player_uid):
        """Remove a player from a group"""
        group = PlayerGroup.nodes.get(uid=group_uid)
        owner = Player.nodes.get(uid=owner_uid)
        player = Player.nodes.get(uid=player_uid)

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
    def leave_group(group_uid, player_uid):
        """Leave a group"""
        group = PlayerGroup.nodes.get(uid=group_uid)
        player = Player.nodes.get(uid=player_uid)

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
    def delete_group(group_uid, owner_uid):
        """Delete a group"""
        group = PlayerGroup.nodes.get(uid=group_uid)
        owner = Player.nodes.get(uid=owner_uid)

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
            PlayerGroupService.send_group_deleted_notification(group_uid, member)

        return True

    @staticmethod
    def invite_group_to_game(game_uid, group_uid, inviter_uid):
        """Invite an entire group to a game"""
        game = Game.nodes.get(uid=game_uid)
        group = PlayerGroup.nodes.get(uid=group_uid)
        inviter = Player.nodes.get(uid=inviter_uid)

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
            if member.uid == inviter_uid:
                continue

            # Skip players already in the game
            if game.players.is_connected(member):
                continue

            try:
                # Use the existing invite_player method
                game_player = GameService.invite_player(
                    game_uid=game_uid,
                    player_uid=member.uid,
                    inviter_uid=inviter_uid
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
                'invitation_uid': invitation.uid,
                'group_uid': group.uid,
                'group_name': group.name,
                'inviter_uid': inviter.uid,
                'inviter_username': inviter.username,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the invitee's personal channel
            async_to_sync(channel_layer.group_send)(
                f'user_{invitee.uid}',
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
                'group_uid': group.group_uid,
                'group_name': group.name,
                'user_uid': player.user_uid,
                'username': player.username,
                'response': response,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the group owner's personal channel
            owner = group.owner.get()
            async_to_sync(channel_layer.group_send)(
                f'user_{owner.user_uid}',
                {
                    'type': 'group_invitation_response',
                    'data': response_data
                }
            )

            # If accepted, notify all group members
            if response == 'accepted':
                for member in group.members.all():
                    if member.user_uid != player.user_uid and member.user_uid != owner.user_uid:
                        async_to_sync(channel_layer.group_send)(
                            f'user_{member.user_uid}',
                            {
                                'type': 'group_member_joined',
                                'data': {
                                    'group_uid': group.group_uid,
                                    'group_name': group.name,
                                    'user_uid': player.user_uid,
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
                'group_uid': group.group_uid,
                'group_name': group.name,
                'user_uid': player.user_uid,
                'username': player.username,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the removed player
            async_to_sync(channel_layer.group_send)(
                f'user_{player.user_uid}',
                {
                    'type': 'group_removed_from',
                    'data': notification_data
                }
            )

            # Notify all remaining group members
            for member in group.members.all():
                if member.user_uid != player.user_uid:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member.user_uid}',
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
                'group_uid': group.group_uid,
                'group_name': group.name,
                'user_uid': player.user_uid,
                'username': player.username,
                'timestamp': datetime.now().isoformat()
            }

            # Notify all remaining group members
            for member in group.members.all():
                if member.user_uid != player.user_uid:
                    async_to_sync(channel_layer.group_send)(
                        f'user_{member.user_uid}',
                        {
                            'type': 'group_member_left',
                            'data': notification_data
                        }
                    )
        except Exception as e:
            print(f"Error sending group member left notification: {str(e)}")

    @staticmethod
    def send_group_deleted_notification(group_uid, player):
        """Send a notification that a group has been deleted"""
        try:
            channel_layer = get_channel_layer()

            # Prepare the notification data
            notification_data = {
                'group_uid': group_uid,
                'timestamp': datetime.now().isoformat()
            }

            # Send to the player
            async_to_sync(channel_layer.group_send)(
                f'user_{player.uid}',
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
                'game_uid': game.uid,
                'game_type': game.game_type,
                'group_uid': group.uid,
                'group_name': group.name,
                'inviter_uid': inviter.uid,
                'inviter_username': inviter.username,
                'invited_count': len(invited_players),
                'timestamp': datetime.now().isoformat()
            }

            # Send to all group members
            for member in group.members.all():
                # Skip the inviter
                if member.uid == inviter.uid:
                    continue

                async_to_sync(channel_layer.group_send)(
                    f'user_{member.uid}',
                    {
                        'type': 'group_game_invitation',
                        'data': notification_data
                    }
                )
        except Exception as e:
            print(f"Error sending group game invitation notification: {str(e)}")
