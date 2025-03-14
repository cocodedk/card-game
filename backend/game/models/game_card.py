from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    JSONProperty, RelationshipFrom, RelationshipTo, One
)
import uuid

class GameCard(StructuredNode):
    """GameCard model representing a card instance in a game"""
    instance_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    location = StringProperty(choices={
        'deck': 'In deck',
        'hand': 'In hand',
        'field': 'On field',
        'graveyard': 'In graveyard'
    })
    position = IntegerProperty(default=0)
    state = JSONProperty(default={})

    # Relationships
    game = RelationshipFrom('game.models.game.Game', 'HAS_CARD', cardinality=One)
    card = RelationshipTo('game.models.card.Card', 'REPRESENTS', cardinality=One)
    owner = RelationshipTo('game.models.player.Player', 'CONTROLLED_BY', cardinality=One)
