from neomodel import (
    StructuredNode, StringProperty, IntegerProperty,
    DateTimeProperty, BooleanProperty, JSONProperty,
    RelationshipFrom, RelationshipTo, One, ZeroOrOne
)
import uuid
from datetime import datetime

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
    players = RelationshipFrom('game.models.player.Player', 'PARTICIPATES_IN')
    creator = RelationshipTo('game.models.player.Player', 'CREATED_BY', cardinality=One)
    decks = RelationshipTo('game.models.deck.Deck', 'USES')
    current_player = RelationshipTo('game.models.player.Player', 'CURRENT_TURN', cardinality=ZeroOrOne)
    winner = RelationshipTo('game.models.player.Player', 'WON_BY', cardinality=ZeroOrOne)
    game_cards = RelationshipTo('game.models.game_card.GameCard', 'HAS_CARD')
    rule_set = RelationshipTo('game.models.game_rule_set.GameRuleSet', 'USES_RULES', cardinality=One)
    game_players = RelationshipTo('game.models.game_player.GamePlayer', 'HAS_PLAYER')
    invited_groups = RelationshipTo('game.models.player_group.PlayerGroup', 'INVITED_GROUP')
    participating_groups = RelationshipFrom('game.models.player_group.PlayerGroup', 'PARTICIPATED_IN')
    parent_tournament = RelationshipTo('game.models.game.Game', 'PART_OF_TOURNAMENT', cardinality=ZeroOrOne)
    tournament_games = RelationshipFrom('game.models.game.Game', 'PART_OF_TOURNAMENT')
