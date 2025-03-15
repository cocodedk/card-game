from neomodel import (
    StringProperty, ArrayProperty, JSONProperty, RelationshipTo, BooleanProperty
)
from backend.game.models.base import GameBaseModel

class GameState(GameBaseModel):
    """Model to store the current state of a game"""
    current_player_uid = StringProperty(index=True)
    next_player_uid = StringProperty()
    direction = StringProperty(default="clockwise")
    skipped_players = ArrayProperty(StringProperty())
    discard_pile = JSONProperty(default=[])
    draw_pile = JSONProperty(default=[])
    player_states = JSONProperty(default={})
    game_over = BooleanProperty(default=False)
    winner_id = StringProperty()

    # Relationships
    game = RelationshipTo('game.models.game.Game', 'STATE_OF')

    @property
    def current_player(self):
        """Get the current player object"""
        return self.player_states.get(self.current_player_uid, {})

    @property
    def players(self):
        """Get all player objects"""
        return [self.player_states[pid] for pid in self.player_states]

    def draw_card(self):
        """Draw a card from the draw pile"""
        if not self.draw_pile:
            return None
        return self.draw_pile.pop(0)
