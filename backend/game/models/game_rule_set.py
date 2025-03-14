from neomodel import (
    StructuredNode, StringProperty, BooleanProperty,
    DateTimeProperty, JSONProperty, RelationshipFrom
)
from datetime import datetime
import uuid

class GameRuleSet(StructuredNode):
    """GameRuleSet model for configurable game rules"""
    rule_set_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    version = StringProperty(required=True, index=True)
    name = StringProperty(default="Standard Rules")
    description = StringProperty()
    active = BooleanProperty(default=True)
    created_at = DateTimeProperty(default=datetime.now)
    parameters = JSONProperty(default={})

    # Relationships
    games = RelationshipFrom('game.models.game.Game', 'USES_RULES')
