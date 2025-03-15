from neomodel import (
    StringProperty, IntegerProperty,
    JSONProperty, RelationshipFrom
)
from backend.game.models.base import GameBaseModel

class Card(GameBaseModel):
    """Card model representing a game card"""
    name = StringProperty(index=True)
    card_type = StringProperty(index=True)
    rarity = StringProperty(index=True)
    cost = IntegerProperty(default=0)
    attack = IntegerProperty(default=0)
    defense = IntegerProperty(default=0)
    image_url = StringProperty(default="")
    abilities = JSONProperty(default={})

    # Relationships
    owner = RelationshipFrom('game.models.player.Player', 'OWNS')
    decks = RelationshipFrom('game.models.deck.Deck', 'CONTAINS')
    game_instances = RelationshipFrom('game.models.game_card.GameCard', 'REPRESENTS')
