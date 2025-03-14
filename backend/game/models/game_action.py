from neomodel import (
    StructuredNode, StringProperty, DateTimeProperty,
    JSONProperty, RelationshipTo, One, ZeroOrOne
)
import uuid
from datetime import datetime

class GameAction(StructuredNode):
    """GameAction model for tracking game history"""
    action_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    action_type = StringProperty(index=True)
    timestamp = DateTimeProperty(default=datetime.now)
    action_data = JSONProperty()

    # Relationships
    game = RelationshipTo('game.models.game.Game', 'OCCURRED_IN', cardinality=One)
    player = RelationshipTo('game.models.player.Player', 'PERFORMED_BY', cardinality=ZeroOrOne)
    affected_cards = RelationshipTo('game.models.game_card.GameCard', 'AFFECTED')
