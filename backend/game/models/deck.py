from neomodel import (
    StructuredNode, StringProperty, DateTimeProperty,
    RelationshipFrom, RelationshipTo, One
)
import uuid
from datetime import datetime

class Deck(StructuredNode):
    """Deck model representing a collection of cards"""
    deck_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    name = StringProperty(index=True)
    description = StringProperty()
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)

    # Relationships
    creator = RelationshipFrom('game.models.player.Player', 'CREATED', cardinality=One)
    cards = RelationshipTo('game.models.card.Card', 'CONTAINS')
    games = RelationshipFrom('game.models.game.Game', 'USES')
