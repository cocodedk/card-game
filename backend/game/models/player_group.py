from neomodel import (
    StringProperty, BooleanProperty,
    RelationshipFrom, RelationshipTo, One
)
from game.models.base import GameBaseModel

class PlayerGroup(GameBaseModel):
    """PlayerGroup model representing a group of players that can be invited to games together"""
    name = StringProperty(index=True)
    description = StringProperty(default="")
    is_public = BooleanProperty(default=False)
    avatar = StringProperty(default="default_group.png")

    # Relationships
    owner = RelationshipFrom('game.models.player.Player', 'OWNS', cardinality=One)
    members = RelationshipFrom('game.models.player.Player', 'MEMBER_OF')
    games = RelationshipTo('game.models.game.Game', 'PARTICIPATED_IN')
