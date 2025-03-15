
from backend.game.models.game_card import GameCard


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
