from backend.game.models import GameRuleSet

def create_idiot_rule_set(initial_direction="clockwise", cards_per_player=4, min_cards=2, max_cards=8):
    """
    Create a rule set for the Idiot card game

    Args:
        initial_direction (str): Initial direction of play ("clockwise" or "counterclockwise")
        cards_per_player (int): Default number of cards dealt to each player
        min_cards (int): Minimum number of cards that can be dealt
        max_cards (int): Maximum number of cards that can be dealt

    Returns:
        GameRuleSet: The created rule set

    Raises:
        ValueError: If any of the parameters are invalid
    """
    # Validate initial_direction
    if initial_direction not in ["clockwise", "counterclockwise"]:
        raise ValueError("initial_direction must be either 'clockwise' or 'counterclockwise'")

    # Validate card counts
    if cards_per_player <= 0:
        raise ValueError("cards_per_player must be greater than 0")

    if min_cards <= 0:
        raise ValueError("min_cards must be greater than 0")

    if max_cards <= 0:
        raise ValueError("max_cards must be greater than 0")

    if min_cards > max_cards:
        raise ValueError("min_cards cannot be greater than max_cards")

    if cards_per_player < min_cards:
        raise ValueError("cards_per_player cannot be less than min_cards")

    if cards_per_player > max_cards:
        raise ValueError("cards_per_player cannot be greater than max_cards")

    card_actions = {
        # 2: Give a card to the next player
        "hearts_2": {
            "action_type": "give_card",
            "target": "next_player",
            "effect": "give_card",
            "points_if_last": 3
        },
        "diamonds_2": {
            "action_type": "give_card",
            "target": "next_player",
            "effect": "give_card",
            "points_if_last": 3
        },
        "clubs_2": {
            "action_type": "give_card",
            "target": "next_player",
            "effect": "give_card",
            "points_if_last": 3
        },
        "spades_2": {
            "action_type": "give_card",
            "target": "next_player",
            "effect": "give_card",
            "points_if_last": 3
        },

        # 3: Previous player draws a card
        "hearts_3": {
            "action_type": "draw",
            "target": "previous_player",
            "effect": "draw_cards",
            "amount": 1
        },
        "diamonds_3": {
            "action_type": "draw",
            "target": "previous_player",
            "effect": "draw_cards",
            "amount": 1
        },
        "clubs_3": {
            "action_type": "draw",
            "target": "previous_player",
            "effect": "draw_cards",
            "amount": 1
        },
        "spades_3": {
            "action_type": "draw",
            "target": "previous_player",
            "effect": "draw_cards",
            "amount": 1
        },

        # 4: No action
        # 5: No action

        # 6: Second player in queue must draw
        "hearts_6": {
            "action_type": "draw",
            "target": "second_next_player",
            "effect": "draw_cards",
            "amount": 1
        },
        "diamonds_6": {
            "action_type": "draw",
            "target": "second_next_player",
            "effect": "draw_cards",
            "amount": 1
        },
        "clubs_6": {
            "action_type": "draw",
            "target": "second_next_player",
            "effect": "draw_cards",
            "amount": 1
        },
        "spades_6": {
            "action_type": "draw",
            "target": "second_next_player",
            "effect": "draw_cards",
            "amount": 1
        },

        # 7: Next player draws 2 cards (special chain rules with 8 and 10)
        "hearts_7": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2,
            "can_counter": True,
            "counter_cards": ["8", "10"],
            "counter_same_suit": True,
            "chain_action": True
        },
        "diamonds_7": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2,
            "can_counter": True,
            "counter_cards": ["8", "10"],
            "counter_same_suit": True,
            "chain_action": True
        },
        "clubs_7": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2,
            "can_counter": True,
            "counter_cards": ["8", "10"],
            "counter_same_suit": True,
            "chain_action": True
        },
        "spades_7": {
            "action_type": "draw",
            "target": "next_player",
            "effect": "draw_cards",
            "amount": 2,
            "can_counter": True,
            "counter_cards": ["8", "10"],
            "counter_same_suit": True,
            "chain_action": True
        },

        # 8: Skip next player (or counter to 7)
        "hearts_8": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn",
            "counter_to": "7",
            "counter_options": [
                {
                    "effect": "draw_cards",
                    "target": "next_player",
                    "amount": 5,  # 2 from 7 + 3 from 8
                    "description": "Next player draws 5 cards (2+3)"
                },
                {
                    "effect": "draw_cards",
                    "target": "opposite_player",
                    "amount": 2,  # Original penalty from 7
                    "description": "Opposite player draws 2 cards"
                }
            ],
            "chain_counter": {
                "increase_amount": 3,  # Each additional 8 adds 3 more cards
                "or_transfer": "opposite_player"  # Or transfers current penalty to opposite player
            }
        },
        "diamonds_8": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn",
            "counter_to": "7",
            "counter_options": [
                {
                    "effect": "draw_cards",
                    "target": "next_player",
                    "amount": 5,  # 2 from 7 + 3 from 8
                    "description": "Next player draws 5 cards (2+3)"
                },
                {
                    "effect": "draw_cards",
                    "target": "opposite_player",
                    "amount": 2,  # Original penalty from 7
                    "description": "Opposite player draws 2 cards"
                }
            ],
            "chain_counter": {
                "increase_amount": 3,  # Each additional 8 adds 3 more cards
                "or_transfer": "opposite_player"  # Or transfers current penalty to opposite player
            }
        },
        "clubs_8": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn",
            "counter_to": "7",
            "counter_options": [
                {
                    "effect": "draw_cards",
                    "target": "next_player",
                    "amount": 5,  # 2 from 7 + 3 from 8
                    "description": "Next player draws 5 cards (2+3)"
                },
                {
                    "effect": "draw_cards",
                    "target": "opposite_player",
                    "amount": 2,  # Original penalty from 7
                    "description": "Opposite player draws 2 cards"
                }
            ],
            "chain_counter": {
                "increase_amount": 3,  # Each additional 8 adds 3 more cards
                "or_transfer": "opposite_player"  # Or transfers current penalty to opposite player
            }
        },
        "spades_8": {
            "action_type": "skip",
            "target": "next_player",
            "effect": "skip_turn",
            "counter_to": "7",
            "counter_options": [
                {
                    "effect": "draw_cards",
                    "target": "next_player",
                    "amount": 5,  # 2 from 7 + 3 from 8
                    "description": "Next player draws 5 cards (2+3)"
                },
                {
                    "effect": "draw_cards",
                    "target": "opposite_player",
                    "amount": 2,  # Original penalty from 7
                    "description": "Opposite player draws 2 cards"
                }
            ],
            "chain_counter": {
                "increase_amount": 3,  # Each additional 8 adds 3 more cards
                "or_transfer": "opposite_player"  # Or transfers current penalty to opposite player
            }
        },

        # 9 of diamonds: All other players draw a card
        "diamonds_9": {
            "action_type": "draw",
            "target": "all_others",
            "effect": "draw_cards",
            "amount": 1
        },

        # 10: Reverse game direction (or counter to 7)
        "hearts_10": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction",
            "counter_to": "7",
            "counter_effect": "reverse_and_bounce",
            "bounce_target": "previous_player",
            "bounce_amount": 2
        },
        "diamonds_10": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction",
            "counter_to": "7",
            "counter_effect": "reverse_and_bounce",
            "bounce_target": "previous_player",
            "bounce_amount": 2
        },
        "clubs_10": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction",
            "counter_to": "7",
            "counter_effect": "reverse_and_bounce",
            "bounce_target": "previous_player",
            "bounce_amount": 2
        },
        "spades_10": {
            "action_type": "reverse",
            "target": "all",
            "effect": "reverse_direction",
            "counter_to": "7",
            "counter_effect": "reverse_and_bounce",
            "bounce_target": "previous_player",
            "bounce_amount": 2
        },

        # Jack: Choose suit
        "hearts_J": {
            "action_type": "choose_suit",
            "target": "none",
            "effect": "choose_suit",
            "points_if_last": 2
        },
        "diamonds_J": {
            "action_type": "choose_suit",
            "target": "none",
            "effect": "choose_suit",
            "points_if_last": 2
        },
        "clubs_J": {
            "action_type": "choose_suit",
            "target": "none",
            "effect": "choose_suit",
            "points_if_last": 2
        },
        "spades_J": {
            "action_type": "choose_suit",
            "target": "none",
            "effect": "choose_suit",
            "points_if_last": 2
        },

        # Queen: Next player must place a card face up but cannot play it
        "hearts_Q": {
            "action_type": "force_reveal",
            "target": "next_player",
            "effect": "reveal_card_and_draw",
            "description": "Next player must reveal a card but cannot play it, and must draw a card"
        },
        "diamonds_Q": {
            "action_type": "force_reveal",
            "target": "next_player",
            "effect": "reveal_card_and_draw",
            "description": "Next player must reveal a card but cannot play it, and must draw a card"
        },
        "clubs_Q": {
            "action_type": "force_reveal",
            "target": "next_player",
            "effect": "reveal_card_and_draw",
            "description": "Next player must reveal a card but cannot play it, and must draw a card"
        },
        "spades_Q": {
            "action_type": "force_reveal",
            "target": "next_player",
            "effect": "reveal_card_and_draw",
            "description": "Next player must reveal a card but cannot play it, and must draw a card"
        },

        # King: Next player draws a card and is skipped
        "hearts_K": {
            "action_type": "draw_and_skip",
            "target": "next_player",
            "effect": "draw_and_skip",
            "amount": 1
        },
        "diamonds_K": {
            "action_type": "draw_and_skip",
            "target": "next_player",
            "effect": "draw_and_skip",
            "amount": 1
        },
        "clubs_K": {
            "action_type": "draw_and_skip",
            "target": "next_player",
            "effect": "draw_and_skip",
            "amount": 1
        },
        "spades_K": {
            "action_type": "draw_and_skip",
            "target": "next_player",
            "effect": "draw_and_skip",
            "amount": 1
        },

        # Ace: Play another card of same suit (chain action)
        "hearts_A": {
            "action_type": "play_again",
            "target": "self",
            "effect": "play_again",
            "same_suit": True,
            "chain_action": True,
            "chain_with": ["A"]
        },
        "diamonds_A": {
            "action_type": "play_again",
            "target": "self",
            "effect": "play_again",
            "same_suit": True,
            "chain_action": True,
            "chain_with": ["A"]
        },
        "clubs_A": {
            "action_type": "play_again",
            "target": "self",
            "effect": "play_again",
            "same_suit": True,
            "chain_action": True,
            "chain_with": ["A"]
        },
        "spades_A": {
            "action_type": "play_again",
            "target": "self",
            "effect": "play_again",
            "same_suit": True,
            "chain_action": True,
            "chain_with": ["A"]
        }
    }

    targeting_rules = {
        "next_player": {"offset": 1},
        "previous_player": {"offset": -1},
        "second_next_player": {"offset": 2},
        "all": {"type": "all_players"},
        "all_others": {"type": "all_except_current"},
        "self": {"type": "current_player"},
        "none": {"type": "no_target"},
        "player_choice": {"type": "selection", "constraints": ["not_self"]}
    }

    turn_flow = {
        "initial_direction": initial_direction,
        "can_reverse": True,
        "skip_allowed": True,
        "play_again_allowed": True,
        "chain_actions": True
    }

    win_conditions = [
        {"type": "empty_hand", "description": "First player to play all cards wins"},
        {"type": "special_last_card", "description": "Special scoring for last card played"}
    ]

    play_rules = {
        "match_criteria": ["suit", "value"],
        "special_cards": {
            "J": "choose_suit"
        },
        "one_card_announcement": {
            "required": True,
            "penalty": 1
        },
        "equal_sum_penalty": {
            "two_players": -1,
            "three_players": -3
        },
        "last_card_special_points": {
            "2": 3,
            "J": 2,
            "7": "continue_if_countered"
        }
    }

    deck_configuration = {
        "card_types": ["standard"],
        "suits": ["hearts", "diamonds", "clubs", "spades"],
        "values": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    }

    # Add dealing configuration
    dealing_config = {
        "cards_per_player": cards_per_player,
        "min_cards": min_cards,
        "max_cards": max_cards
    }

    # Use the new method specifically for Idiot game
    return GameRuleSet.create_idiot_card_game(
        name="Idiot Card Game",
        description="A complex card game with special actions for each card value",
        card_actions=card_actions,
        targeting_rules=targeting_rules,
        turn_flow=turn_flow,
        win_conditions=win_conditions,
        play_rules=play_rules,
        deck_configuration=deck_configuration,
        dealing_config=dealing_config
    )
