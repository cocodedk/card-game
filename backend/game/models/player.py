from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    DateTimeProperty, RelationshipTo
)
from datetime import datetime
import uuid

class Player(StructuredNode):
    """Player model representing a user in the game context"""
    player_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    user_id = IntegerProperty(unique_index=True)
    username = StringProperty(unique_index=True)
    display_name = StringProperty(default="")
    avatar = StringProperty(default="default_avatar.png")
    created_at = DateTimeProperty(default=datetime.now)
    date_of_birth = StringProperty(default="")
    callsign = StringProperty(default="")

    # Relationships
    games = RelationshipTo('game.models.game.Game', 'PARTICIPATES_IN')
    cards = RelationshipTo('game.models.card.Card', 'OWNS')
    decks = RelationshipTo('game.models.deck.Deck', 'CREATED')
    game_players = RelationshipTo('game.models.game_player.GamePlayer', 'HAS_GAME_PLAYER')
    owned_groups = RelationshipTo('game.models.player_group.PlayerGroup', 'OWNS')
    member_of_groups = RelationshipTo('game.models.player_group.PlayerGroup', 'MEMBER_OF')
