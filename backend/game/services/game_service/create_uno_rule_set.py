from backend.game.models import GameRuleSet

def create_uno_rule_set(initial_direction="clockwise", cards_per_player=7, min_cards=1, max_cards=12):
    """
    Create a rule set for an Uno-like game

    Args:
        initial_direction (str): Initial direction of play ("clockwise" or "counterclockwise")
        cards_per_player (int): Default number of cards dealt to each player
        min_cards (int): Minimum number of cards that can be dealt
        max_cards (int): Maximum number of cards that can be dealt

    Returns:
        GameRuleSet: The created rule set
    """
    card_actions = {
        "hearts_2": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2
        },
        "diamonds_2": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2
        },
        "clubs_2": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2
        },
        "spades_2": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2
        },
        "hearts_A": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn"
        },
        "diamonds_A": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn"
        },
        "clubs_A": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn"
        },
        "spades_A": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn"
        },
        "hearts_K": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction"
        },
        "diamonds_K": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction"
        },
        "clubs_K": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction"
        },
        "spades_K": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction"
        },
        "special_wild": {
            "action_type": "choose",
            "target": "player_choice",
            "effect": "choose_next_player"
        }
    }

    targeting_rules = {
        "next_player": {"offset": 1},
        "previous_player": {"offset": -1},
        "opposite_player": {"offset": "players_count / 2"},
        "all": {"type": "all_players"},
        "player_choice": {"type": "selection", "constraints": ["not_self"]}
    }

    turn_flow = {
        "initial_direction": initial_direction,
        "can_reverse": True,
        "skip_allowed": True
    }

    win_conditions = [
        {"type": "empty_hand", "description": "First player to play all cards wins"}
    ]

    deck_configuration = {
        "card_types": ["standard", "special"],
        "suits": ["hearts", "diamonds", "clubs", "spades"],
        "values": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"],
        "special_cards": [
            {"type": "wild", "value": "wild", "count": 4}
        ]
    }

    # Add dealing configuration
    dealing_config = {
        "cards_per_player": cards_per_player,
        "min_cards": min_cards,
        "max_cards": max_cards
    }

    return GameRuleSet.create_action_card_game(
        name="Uno-like Game",
        description="A game similar to Uno with action cards",
        card_actions=card_actions,
        targeting_rules=targeting_rules,
        turn_flow=turn_flow,
        win_conditions=win_conditions,
        deck_configuration=deck_configuration,
        dealing_config=dealing_config
    )
