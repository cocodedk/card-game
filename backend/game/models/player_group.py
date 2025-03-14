from neomodel import (
    StructuredNode, StringProperty, BooleanProperty,
    DateTimeProperty, RelationshipFrom, RelationshipTo, One
)
import uuid
from datetime import datetime

class PlayerGroup(StructuredNode):
    """PlayerGroup model representing a group of players that can be invited to games together"""
    group_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    name = StringProperty(index=True)
    description = StringProperty(default="")
    is_public = BooleanProperty(default=False)
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)
    avatar = StringProperty(default="default_group.png")

    # Relationships
    owner = RelationshipFrom('game.models.player.Player', 'OWNS', cardinality=One)
    members = RelationshipFrom('game.models.player.Player', 'MEMBER_OF')
    games = RelationshipTo('game.models.game.Game', 'PARTICIPATED_IN')
