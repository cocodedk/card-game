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
    games = RelationshipTo('game.models.game.Game', 'PARTICIPATES_IN')
    cards = RelationshipTo('game.models.card.Card', 'OWNS')
    decks = RelationshipTo('game.models.deck.Deck', 'CREATED')
    game_players = RelationshipTo('game.models.game_player.GamePlayer', 'HAS_GAME_PLAYER')
    owned_groups = RelationshipTo('game.models.player_group.PlayerGroup', 'OWNS')
    member_of_groups = RelationshipTo('game.models.player_group.PlayerGroup', 'MEMBER_OF')
