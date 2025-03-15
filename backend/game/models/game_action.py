from neomodel import (
    StringProperty,
    JSONProperty, RelationshipTo, One, ZeroOrOne
)
from game.models.base import GameBaseModel

class GameAction(GameBaseModel):
    """GameAction model for tracking game history"""
    action_type = StringProperty(index=True)
    action_data = JSONProperty()

    # Relationships
    game = RelationshipTo('game.models.game.Game', 'OCCURRED_IN', cardinality=One)
    player = RelationshipTo('game.models.player.Player', 'PERFORMED_BY', cardinality=ZeroOrOne)
    affected_cards = RelationshipTo('game.models.game_card.GameCard', 'AFFECTED')
