from datetime import datetime
from backend.game.models import Game, GameRuleSet, GamePlayer, GameState, Player
from backend.game.services.game_service_utils.action import Action
from backend.game.services.game_service_utils.create_game_card import create_game_card
from backend.game.services.game_service_utils.create_deck import create_deck

def create_action_card_game(name, player_uids, rule_set_uid):
    """
    Create a new action card game

    Args:
        name (str): Name of the game
        player_uids (list): List of player uids
        rule_set_uid (str): uid of the rule set to use

    Returns:
        dict: Created game information
    """
    # Get the rule set
    rule_set = GameRuleSet.nodes.get(uid=rule_set_uid)

    # Create a new game
    game = Game(
        name=name,
        game_type='standard',
        status='created',
        max_players=len(player_uids),
        started_at=datetime.now()
    ).save()

    # Link the rule set
    game.rule_set.connect(rule_set)

    # Create the initial game state
    deck_config = rule_set.parameters.get("deck_configuration", {})
    dealing_config = rule_set.parameters.get("dealing_config", {"cards_per_player": 7})

    # Get initial direction from rule set
    turn_flow = rule_set.parameters.get("turn_flow", {})
    initial_direction = turn_flow.get("initial_direction", "clockwise")

    # Create the deck
    deck = create_deck(deck_config, game)

    # Shuffle the deck
    import random
    random.shuffle(deck)

    # Get player objects and create GamePlayer instances
    players = []
    for player_uid in player_uids:
        player = Player.nodes.get(uid=player_uid)

        # Create GamePlayer instance
        game_player = GamePlayer(
            status='accepted',
            joined_at=datetime.now()
        ).save()

        # Connect relationships
        game_player.game.connect(game)
        game_player.player.connect(player)
        game.game_players.connect(game_player)

        players.append(player)

    # Deal cards to players
    player_states = {}
    cards_per_player = dealing_config.get("cards_per_player", 7)

    for player in players:
        hand = []
        for _ in range(cards_per_player):
            if deck:
                card_data = deck.pop(0)
                # Create a GameCard for each card in hand
                game_card = create_game_card(game, card_data, player, 'hand')
                hand.append({
                    "id": game_card.uid,
                    "suit": card_data["suit"],
                    "value": card_data["value"]
                })

        player_states[player.uid] = {
            "id": player.uid,
            "hand": hand,
            "score": 0
        }

    # Add a card to discard pile
    first_card = deck.pop(0)
    discard_game_card = create_game_card(game, first_card, None, 'field')
    discard_pile = [{
        "id": discard_game_card.uid,
        "suit": first_card["suit"],
        "value": first_card["value"]
    }]

    # Store remaining deck as draw pile
    draw_pile = []
    for card_data in deck:
        game_card = create_game_card(game, card_data, None, 'deck')
        draw_pile.append({
            "id": game_card.uid,
            "suit": card_data["suit"],
            "value": card_data["value"]
        })

    # Create the game state
    game_state = GameState(
        current_player_uid=players[0].uid,
        direction=initial_direction,
        skipped_players=[],
        discard_pile=discard_pile,
        draw_pile=draw_pile,
        player_states=player_states
    ).save()

    # Link the game state to the game
    game_state.game.connect(game)

    # Set current player
    game.current_player.connect(players[0])

    # Update game status
    game.status = "in_progress"
    game.save()

    return {
        "game_id": game.uid,
        "rule_set": rule_set.name,
        "players": [p.uid for p in players],
        "current_player": players[0].uid,
        "status": "in_progress"
    }
