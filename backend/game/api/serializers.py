from rest_framework import serializers
from backend.game.models import Game, GameState
from backend.game.models.player import Player


class PlayerSerializer(serializers.Serializer):
    """Serializer for player data"""
    uid = serializers.CharField()
    username = serializers.CharField()
    avatar = serializers.CharField(required=False, allow_null=True)


class CardSerializer(serializers.Serializer):
    """Serializer for card data"""
    suit = serializers.CharField()
    rank = serializers.CharField()
    value = serializers.IntegerField()


class PlayerStateSerializer(serializers.Serializer):
    """Serializer for player state in a game"""
    player_id = serializers.CharField(source='uid')
    username = serializers.CharField()
    hand = CardSerializer(many=True, required=False)
    hand_count = serializers.IntegerField(required=False)
    score = serializers.IntegerField(required=False)
    announced_one_card = serializers.BooleanField(default=False)
    is_current_player = serializers.BooleanField(default=False)
    is_next_player = serializers.BooleanField(default=False)


class GameStateSerializer(serializers.Serializer):
    """Serializer for game state"""
    game_id = serializers.CharField(source='game.uid')
    game_name = serializers.CharField(source='game.name')
    status = serializers.CharField(source='game.status')
    current_player = serializers.CharField(source='current_player_uid')
    next_player = serializers.CharField(source='next_player_uid')
    direction = serializers.IntegerField()
    players = PlayerStateSerializer(many=True)
    discard_pile = CardSerializer(many=True)
    top_card = CardSerializer(required=False)
    draw_pile_count = serializers.IntegerField()
    current_suit = serializers.CharField(required=False, allow_null=True)
    skipped_players = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class GameSerializer(serializers.Serializer):
    """Serializer for game data"""
    uid = serializers.CharField()
    name = serializers.CharField()
    status = serializers.CharField()
    creator_id = serializers.CharField()
    players = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    rule_set_id = serializers.CharField(source='rule_set.get.uid')


class GameRuleSetSerializer(serializers.Serializer):
    """Serializer for game rule set data"""
    uid = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(required=False)
    parameters = serializers.DictField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
