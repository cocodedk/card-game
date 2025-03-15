
import uuid

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
