from neomodel import (
    StringProperty, BooleanProperty,
    DateTimeProperty, RelationshipFrom, One
)
from datetime import datetime
from game.models.base import GameBaseModel

class GamePlayer(GameBaseModel):
    """GamePlayer model representing a player in a specific game"""
    is_ai = BooleanProperty(default=False)
    ai_difficulty = StringProperty(choices={
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard',
        'expert': 'Expert'
    }, default=None)
    joined_at = DateTimeProperty(default=datetime.now)
    status = StringProperty(choices={
        'invited': 'Invited',
        'accepted': 'Accepted',
        'declined': 'Declined',
        'left': 'Left'
    }, default='invited')

    # Relationships
    game = RelationshipFrom('game.models.game.Game', 'HAS_PLAYER', cardinality=One)
    player = RelationshipFrom('game.models.player.Player', 'HAS_GAME_PLAYER', cardinality=One)
