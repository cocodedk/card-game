from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    DateTimeProperty, BooleanProperty, JSONProperty,
    RelationshipTo, RelationshipFrom,
    One, ZeroOrOne
)
import uuid
from datetime import datetime

class Player(StructuredNode):
    """Player model representing a user in the game context"""
    user_id = IntegerProperty(unique_index=True)
    username = StringProperty(unique_index=True)
    display_name = StringProperty(default="")
    avatar = StringProperty(default="default_avatar.png")
    created_at = DateTimeProperty(default=datetime.now)
    date_of_birth = StringProperty(default="")
    callsign = StringProperty(default="")

    # Relationships
    games = RelationshipTo('Game', 'PARTICIPATES_IN')
    cards = RelationshipTo('Card', 'OWNS')
    decks = RelationshipTo('Deck', 'CREATED')
    game_players = RelationshipTo('GamePlayer', 'HAS_GAME_PLAYER')
    owned_groups = RelationshipTo('PlayerGroup', 'OWNS')
    member_of_groups = RelationshipTo('PlayerGroup', 'MEMBER_OF')

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
    game_type = StringProperty(choices={
        'standard': 'Standard Game',
        'quick': 'Quick Game',
        'tournament': 'Tournament Game'
    }, default='standard')
    max_players = IntegerProperty(default=2)
    time_limit = IntegerProperty(default=30)  # in minutes
    use_ai = BooleanProperty(default=False)
    status = StringProperty(choices={
        'created': 'Created',
        'waiting': 'Waiting for players',
        'in_progress': 'In progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
    }, default='created')
    current_turn = IntegerProperty(default=0)
    created_at = DateTimeProperty(default=datetime.now)
    started_at = DateTimeProperty()
    ended_at = DateTimeProperty()
    completed_at = DateTimeProperty()
    game_data = JSONProperty(default={})
    rule_version = StringProperty(default="1.0")
    is_tournament = BooleanProperty(default=False)
    tournament_round = IntegerProperty(default=0)
    tournament_data = JSONProperty(default={})

    # Relationships
    players = RelationshipFrom('Player', 'PARTICIPATES_IN')
    creator = RelationshipTo('Player', 'CREATED_BY', cardinality=One)
    decks = RelationshipTo('Deck', 'USES')
    current_player = RelationshipTo('Player', 'CURRENT_TURN', cardinality=ZeroOrOne)
    winner = RelationshipTo('Player', 'WON_BY', cardinality=ZeroOrOne)
    game_cards = RelationshipTo('GameCard', 'HAS_CARD')
    rule_set = RelationshipTo('GameRuleSet', 'USES_RULES', cardinality=One)
    game_players = RelationshipTo('GamePlayer', 'HAS_PLAYER')
    invited_groups = RelationshipTo('PlayerGroup', 'INVITED_GROUP')
    participating_groups = RelationshipFrom('PlayerGroup', 'PARTICIPATED_IN')
    parent_tournament = RelationshipTo('Game', 'PART_OF_TOURNAMENT', cardinality=ZeroOrOne)
    tournament_games = RelationshipFrom('Game', 'PART_OF_TOURNAMENT')

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

class GamePlayer(StructuredNode):
    """GamePlayer model representing a player in a specific game"""
    player_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
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
    game = RelationshipFrom('Game', 'HAS_PLAYER', cardinality=One)
    player = RelationshipFrom('Player', 'HAS_GAME_PLAYER', cardinality=One)

class PlayerGroup(StructuredNode):
    """PlayerGroup model representing a group of players that can be invited to games together"""
    group_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    name = StringProperty(index=True)
    description = StringProperty(default="")
    is_public = BooleanProperty(default=False)
    created_at = DateTimeProperty(default=datetime.now)
    updated_at = DateTimeProperty(default=datetime.now)
    avatar = StringProperty(default="default_group.png")

    # Relationships
    owner = RelationshipFrom('Player', 'OWNS', cardinality=One)
    members = RelationshipFrom('Player', 'MEMBER_OF')
    games = RelationshipTo('Game', 'PARTICIPATED_IN')

class PlayerGroupInvitation(StructuredNode):
    """Invitation to join a player group"""
    invitation_id = StringProperty(unique_index=True, default=lambda: str(uuid.uuid4()))
    created_at = DateTimeProperty(default=datetime.now)
    status = StringProperty(choices={
        'pending': 'Pending',
        'accepted': 'Accepted',
        'declined': 'Declined'
    }, default='pending')

    # Relationships
    group = RelationshipTo('PlayerGroup', 'FOR_GROUP', cardinality=One)
    inviter = RelationshipTo('Player', 'SENT_BY', cardinality=One)
    invitee = RelationshipTo('Player', 'SENT_TO', cardinality=One)
