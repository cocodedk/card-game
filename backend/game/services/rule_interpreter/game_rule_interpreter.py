from abc import ABC, abstractmethod

class GameRuleInterpreter(ABC):
    """Base abstract class for game rule interpreters"""

    def __init__(self, rule_set):
        """
        Initialize with a GameRuleSet instance

        Args:
            rule_set (GameRuleSet): The rule set to interpret
        """
        self.rule_set = rule_set
        self.parameters = rule_set.parameters

    @abstractmethod
    def validate_action(self, game_state, player, action):
        """
        Validate if an action is allowed based on rules

        Args:
            game_state: Current state of the game
            player: Player attempting the action
            action: Action being attempted

        Returns:
            bool: Whether the action is valid
        """
        pass

    @abstractmethod
    def apply_rules(self, game_state):
        """
        Apply rules to the current game state

        Args:
            game_state: Current state of the game

        Returns:
            Updated game state
        """
        pass

    @abstractmethod
    def process_card_play(self, game_state, player, card):
        """
        Process a card being played

        Args:
            game_state: Current state of the game
            player: Player playing the card
            card: Card being played

        Returns:
            Updated game state
        """
        pass
