from backend.game.models import (
    Game, GameRuleSet, GameState, Player,
    GameCard, GamePlayer, GameAction
)
from backend.game.services.rule_interpreter import get_rule_interpreter
import uuid
from datetime import datetime

class Action:
    """Class to represent a player action"""
    def __init__(self, type, **kwargs):
        self.type = type
        for key, value in kwargs.items():
            setattr(self, key, value)

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

def create_game_card(game, card_data, player, location):
    """
    Create a GameCard instance

    Args:
        game (Game): Game instance
        card_data (dict): Card data
        player (Player): Player who owns the card (or None)
        location (str): Card location

    Returns:
        GameCard: Created game card
    """
    game_card = GameCard(
        location=location,
        state={
            "suit": card_data["suit"],
            "value": card_data["value"]
        }
    ).save()

    # Connect relationships
    game.game_cards.connect(game_card)

    if player:
        game_card.owner.connect(player)

    return game_card

def create_deck(deck_config, game):
    """
    Create a deck based on configuration

    Args:
        deck_config (dict): Deck configuration
        game (Game): Game instance for which to create the deck

    Returns:
        list: List of card data dictionaries
    """
    deck = []

    card_types = deck_config.get("card_types", ["standard"])
    suits = deck_config.get("suits", ["hearts", "diamonds", "clubs", "spades"])
    values = deck_config.get("values", ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"])

    # Create standard cards
    if "standard" in card_types:
        for suit in suits:
            for value in values:
                deck.append({
                    "id": str(uuid.uuid4()),
                    "suit": suit,
                    "value": value
                })

    # Create special cards if needed
    if "special" in card_types:
        special_cards = deck_config.get("special_cards", [])
        for special in special_cards:
            count = special.get("count", 1)
            for _ in range(count):
                deck.append({
                    "id": str(uuid.uuid4()),
                    "suit": f"special_{special['type']}",
                    "value": special.get("value", "special")
                })

    return deck

def play_card(game_uid, player_uid, card_uid):
    """
    Handle a player playing a card

    Args:
        game_id (str): ID of the game
        player_uid (str): ID of the player
        card_uid (str): ID of the card (GameCard uid)

    Returns:
        dict: Result of the action
    """
    # Get the game
    game = Game.nodes.get(uid=game_uid)

    # Check game status
    if game.status != "in_progress":
        return {"error": "Game is not active"}

    # Get the rule set
    rule_set = game.rule_set.single()

    # Get the rule interpreter
    interpreter = get_rule_interpreter(rule_set)

    # Get the game state
    game_state = GameState.nodes.filter(game=game).first()

    # Check if it's the player's turn
    if game_state.current_player_uid != player_uid:
        return {"error": "Not your turn"}

    # Get the player
    player = Player.nodes.get(uid=player_uid)
    player_state = game_state.player_states.get(player_uid)
    if not player_state:
        return {"error": "Player not found in game state"}

    # Get the game card
    game_card = GameCard.nodes.get(uid=card_uid)

    # Find the card in player's hand
    card_data = next((c for c in player_state["hand"] if c["id"] == card_uid), None)
    if not card_data:
        return {"error": "Card not in player's hand"}

    # Create action object for validation
    class Action:
        def __init__(self, type, card):
            self.type = type
            self.card = card

    class CardObj:
        def __init__(self, id, suit, value):
            self.id = id
            self.suit = suit
            self.value = value

        def __eq__(self, other):
            if not isinstance(other, CardObj):
                return False
            return self.id == other.id

    card_obj = CardObj(card_data["id"], card_data["suit"], card_data["value"])
    action = Action(type="play_card", card=card_obj)

    # Validate the action
    if interpreter.validate_action(game_state, player_state, action):
        # Process the card play
        updated_state = interpreter.process_card_play(game_state, player_state, card_obj)

        # Apply any additional rules
        final_state = interpreter.apply_rules(updated_state)

        # Update the game card location
        game_card.location = 'field'
        game_card.save()

        # Record the action
        GameAction(
            action_type="play_card",
            action_data={
                "card_uid": card_uid,
                "player_uid": player_uid,
                "card_suit": card_data["suit"],
                "card_value": card_data["value"]
            }
        ).save().game.connect(game).player.connect(player).affected_cards.connect(game_card)

        # Save the updated state
        for key, value in vars(final_state).items():
            if key != 'id' and not key.startswith('_'):
                setattr(game_state, key, value)
        game_state.save()

        # Check if game is over
        if final_state.game_over:
            game.status = "completed"
            if final_state.winner_id:
                winner = Player.nodes.get(uid=final_state.winner_id)
                game.winner.connect(winner)
            game.completed_at = datetime.now()
            game.ended_at = datetime.now()
            game.save()

            return {
                "success": True,
                "game_over": True,
                "winner": final_state.winner_id
            }

        # Update current player
        next_player = Player.nodes.get(uid=final_state.next_player_uid)
        game.current_player.disconnect_all()
        game.current_player.connect(next_player)

        # Update game state
        game_state.current_player_uid = final_state.next_player_uid
        game_state.next_player_uid = None
        game_state.save()

        return {
            "success": True,
            "next_player": final_state.next_player_uid
        }
    else:
        return {"error": "Invalid card play"}

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
    """
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
