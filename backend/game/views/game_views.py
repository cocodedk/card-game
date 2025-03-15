from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from backend.game.services.game_service_utils import (
    create_action_card_game, play_card, create_uno_rule_set
)
from backend.game.models.game_rule_set import GameRuleSet

@csrf_exempt
@require_http_methods(["POST"])
def create_game(request):
    """Create a new game"""
    try:
        data = json.loads(request.body)
        name = data.get('name', 'New Game')
        players = data.get('players', [])
        rule_set_id = data.get('rule_set_id')

        if not rule_set_id:
            # Create a default rule set if none provided
            rule_set = create_uno_rule_set()
            rule_set_id = rule_set.uid

        if not players:
            return JsonResponse({"error": "Players are required"}, status=400)

        result = create_action_card_game(name, players, rule_set_id)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def play_card_view(request, game_id):
    """Play a card in a game"""
    try:
        data = json.loads(request.body)
        player_uid = data.get('player_uid')
        card_uid = data.get('card_uid')

        if not player_uid or not card_uid:
            return JsonResponse({"error": "Player ID and Card ID are required"}, status=400)

        result = play_card(game_id, player_uid, card_uid)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def list_rule_sets(request):
    """List available rule sets"""
    try:
        rule_sets = GameRuleSet.nodes.filter(active=True)
        result = [{
            "id": rs.uid,
            "name": rs.name,
            "description": rs.description,
            "version": rs.version
        } for rs in rule_sets]
        return JsonResponse({"rule_sets": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_rule_set(request):
    """Create a custom rule set"""
    try:
        data = json.loads(request.body)
        name = data.get('name', 'Custom Rules')
        description = data.get('description', '')
        card_actions = data.get('card_actions', {})
        targeting_rules = data.get('targeting_rules', {})
        turn_flow = data.get('turn_flow', {})
        win_conditions = data.get('win_conditions', [])
        deck_configuration = data.get('deck_configuration', None)

        rule_set = GameRuleSet.create_action_card_game(
            name=name,
            description=description,
            card_actions=card_actions,
            targeting_rules=targeting_rules,
            turn_flow=turn_flow,
            win_conditions=win_conditions,
            deck_configuration=deck_configuration
        )

        return JsonResponse({
            "id": rule_set.uid,
            "name": rule_set.name,
            "description": rule_set.description,
            "version": rule_set.version
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
