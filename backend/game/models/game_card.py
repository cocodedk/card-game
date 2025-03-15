from neomodel import (
    StringProperty, IntegerProperty,
    JSONProperty, RelationshipFrom, RelationshipTo, One
)
from game.models.base import GameBaseModel

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
    game = RelationshipFrom('game.models.game.Game', 'HAS_CARD', cardinality=One)
    card = RelationshipTo('game.models.card.Card', 'REPRESENTS', cardinality=One)
    owner = RelationshipTo('game.models.player.Player', 'CONTROLLED_BY', cardinality=One)
