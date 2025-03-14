from neomodel import (
    StructuredNode, StringProperty, DateTimeProperty,
    RelationshipTo, One
)
import uuid
from datetime import datetime

class PlayerGroupInvitation(StructuredNode):
    """Invitation to join a player group"""
    invitation_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    created_at = DateTimeProperty(default=datetime.now)
    status = StringProperty(choices={
        'pending': 'Pending',
        'accepted': 'Accepted',
        'declined': 'Declined'
    }, default='pending')

    # Relationships
    group = RelationshipTo('game.models.player_group.PlayerGroup', 'FOR_GROUP', cardinality=One)
    inviter = RelationshipTo('game.models.player.Player', 'SENT_BY', cardinality=One)
    invitee = RelationshipTo('game.models.player.Player', 'SENT_TO', cardinality=One)
