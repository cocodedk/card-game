from neomodel import (
    StructuredNode, StringProperty,
    RelationshipFrom, RelationshipTo, One
)
from backend.game.models.base import GameBaseModel

class Deck(GameBaseModel):
    """Deck model representing a collection of cards"""
    name = StringProperty(index=True)
    description = StringProperty()

    # Relationships
    creator = RelationshipFrom('backend.game.models.player.Player', 'CREATED', cardinality=One)
    cards = RelationshipTo('backend.game.models.card.Card', 'CONTAINS')
    games = RelationshipFrom('backend.game.models.game.Game', 'USES')
