from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    DateTimeProperty, BooleanProperty, JSONProperty,
    RelationshipTo, RelationshipFrom, Relationship,
    One, ZeroOrOne, ZeroOrMore
)
from django.contrib.auth.models import User
import uuid
from datetime import datetime

class Player(StructuredNode):
    """Player model representing a user in the game context"""
    user_id = IntegerProperty(unique_index=True)
    username = StringProperty(unique_index=True)
    display_name = StringProperty(default="")
    avatar = StringProperty(default="default_avatar.png")
    created_at = DateTimeProperty(default=datetime.now)

    # Relationships
    games = RelationshipTo('Game', 'PARTICIPATES_IN')
    cards = RelationshipTo('Card', 'OWNS')
    decks = RelationshipTo('Deck', 'CREATED')

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
    owner = RelationshipFrom('Player', 'OWNS')
    decks = RelationshipFrom('Deck', 'CONTAINS')
    game_instances = RelationshipFrom('GameCard', 'REPRESENTS')

class Deck(StructuredNode):
    """Deck model representing a collection of cards"""
    deck_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    name = StringProperty(index=True)
    description = StringProperty()
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)

    # Relationships
    creator = RelationshipFrom('Player', 'CREATED', cardinality=One)
    cards = RelationshipTo('Card', 'CONTAINS')
    games = RelationshipFrom('Game', 'USES')

class Game(StructuredNode):
    """Game model representing a game session"""
    game_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    status = StringProperty(choices={
        'waiting': 'Waiting for players',
        'in_progress': 'In progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }, default='waiting')
    current_turn = IntegerProperty(default=0)
    created_at = DateTimeProperty(default=datetime.now)
    started_at = DateTimeProperty()
    ended_at = DateTimeProperty()
    game_data = JSONProperty(default={})
    rule_version = StringProperty(default="1.0")

    # Relationships
    players = RelationshipFrom('Player', 'PARTICIPATES_IN')
    decks = RelationshipTo('Deck', 'USES')
    current_player = RelationshipTo('Player', 'CURRENT_TURN', cardinality=ZeroOrOne)
    winner = RelationshipTo('Player', 'WON_BY', cardinality=ZeroOrOne)
    game_cards = RelationshipTo('GameCard', 'HAS_CARD')
    rule_set = RelationshipTo('GameRuleSet', 'USES_RULES', cardinality=One)

class GameCard(StructuredNode):
    """GameCard model representing a card instance in a game"""
    instance_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    location = StringProperty(choices={
        'deck': 'In deck',
        'hand': 'In hand',
        'field': 'On field',
        'graveyard': 'In graveyard'
    })
    position = IntegerProperty(default=0)
    state = JSONProperty(default={})

    # Relationships
    game = RelationshipFrom('Game', 'HAS_CARD', cardinality=One)
    card = RelationshipTo('Card', 'REPRESENTS', cardinality=One)
    owner = RelationshipTo('Player', 'CONTROLLED_BY', cardinality=One)

class GameRuleSet(StructuredNode):
    """GameRuleSet model for configurable game rules"""
    version = StringProperty(required=True, index=True)
    name = StringProperty(default="Standard Rules")
    description = StringProperty()
    active = BooleanProperty(default=True)
    created_at = DateTimeProperty(default=datetime.now)
    parameters = JSONProperty(default={})

    # Relationships
    games = RelationshipFrom('Game', 'USES_RULES')

class GameAction(StructuredNode):
    """GameAction model for tracking game history"""
    action_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    action_type = StringProperty(index=True)
    timestamp = DateTimeProperty(default=datetime.now)
    action_data = JSONProperty()

    # Relationships
    game = RelationshipTo('Game', 'OCCURRED_IN', cardinality=One)
    player = RelationshipTo('Player', 'PERFORMED_BY', cardinality=ZeroOrOne)
    affected_cards = RelationshipTo('GameCard', 'AFFECTED')
