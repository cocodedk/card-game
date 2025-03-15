from neomodel import (
    StringProperty, IntegerProperty,
    JSONProperty, RelationshipFrom, RelationshipTo, One
)
from backend.game.models.base import GameBaseModel

class GameCard(GameBaseModel):
    """GameCard model representing a card instance in a game"""
    location = StringProperty(choices={
        'deck': 'In deck',
        'hand': 'In hand',
        'field': 'On field',
        'graveyard': 'In graveyard'
    })
    position = IntegerProperty(default=0)
    state = JSONProperty(default={})

    # Relationships
    game = RelationshipFrom('backend.game.models.game.Game', 'HAS_CARD', cardinality=One)
    card = RelationshipTo('backend.game.models.card.Card', 'REPRESENTS', cardinality=One)
    owner = RelationshipTo('backend.game.models.player.Player', 'CONTROLLED_BY', cardinality=One)
