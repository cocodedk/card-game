from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    JSONProperty, RelationshipFrom
)
import uuid

class Card(StructuredNode):
    """Card model representing a game card"""
    card_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
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
