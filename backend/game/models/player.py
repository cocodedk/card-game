from neomodel import (
    StringProperty,
    RelationshipTo
)
from backend.game.models.base import GameBaseModel

class Player(GameBaseModel):
    """Player model representing a user in the game context"""
    username = StringProperty(unique_index=True)
    display_name = StringProperty(default="")
    avatar = StringProperty(default="default_avatar.png")
    date_of_birth = StringProperty(default="")
    callsign = StringProperty(default="")

    # Relationships
    games = RelationshipTo('backend.game.models.game.Game', 'PARTICIPATES_IN')
    cards = RelationshipTo('backend.game.models.card.Card', 'OWNS')
    decks = RelationshipTo('backend.game.models.deck.Deck', 'CREATED')
    game_players = RelationshipTo('backend.game.models.game_player.GamePlayer', 'HAS_GAME_PLAYER')
    owned_groups = RelationshipTo('backend.game.models.player_group.PlayerGroup', 'OWNS')
    member_of_groups = RelationshipTo('backend.game.models.player_group.PlayerGroup', 'MEMBER_OF')
