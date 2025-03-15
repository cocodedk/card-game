from neomodel import (
    StringProperty,
    RelationshipTo, One
)
from game.models.base import GameBaseModel

class PlayerGroupInvitation(GameBaseModel):
    """Invitation to join a player group"""
    status = StringProperty(choices={
        'pending': 'Pending',
        'accepted': 'Accepted',
        'declined': 'Declined'
    }, default='pending')

    # Relationships
    group = RelationshipTo('game.models.player_group.PlayerGroup', 'FOR_GROUP', cardinality=One)
    inviter = RelationshipTo('game.models.player.Player', 'SENT_BY', cardinality=One)
    invitee = RelationshipTo('game.models.player.Player', 'SENT_TO', cardinality=One)
