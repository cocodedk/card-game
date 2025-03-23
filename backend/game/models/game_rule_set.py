from neomodel import (
    StructuredNode, StringProperty, BooleanProperty,
    DateTimeProperty, JSONProperty, RelationshipFrom
)
from datetime import datetime
import uuid
from backend.game.models.base import GameBaseModel

class GameRuleSet(GameBaseModel):
    """GameRuleSet model for configurable game rules"""
    version = StringProperty(required=True, index=True)
    name = StringProperty(default="Standard Rules", unique_index=True)
    description = StringProperty()
    active = BooleanProperty(default=True)
    created_at = DateTimeProperty(default=datetime.now)
    parameters = JSONProperty(default={})

    # Relationships
    games = RelationshipFrom('backend.game.models.game.Game', 'USES_RULES')

    def save(self):
        """Override save method to check name uniqueness"""
        # Check if a rule set with this name already exists
        if self.uid is None:  # Only check on new instances
            existing = self.__class__.nodes.filter(name=self.name)
            if existing and len(existing) > 0:
                raise ValueError(f"A rule set with name '{self.name}' already exists")
        else:
            # check if another rule set with the same name and another uid exists
            existing = self.__class__.nodes.filter(name=self.name, uid__ne=self.uid)
            if existing and len(existing) > 0:
                raise ValueError(f"A rule set with name '{self.name}' already exists")
        return super().save()

    @classmethod
    def create_action_card_game(cls, name, description, card_actions, targeting_rules,
                               turn_flow, win_conditions, deck_configuration=None, dealing_config=None):
        """
        Create a rule set for an action card game

        Args:
            name (str): Name of the rule set
            description (str): Description of the rule set
            card_actions (dict): Mapping of cards to their actions
            targeting_rules (dict): Rules for targeting players
            turn_flow (dict): Rules for turn progression
            win_conditions (list): Conditions that determine a winner
            deck_configuration (dict, optional): Configuration for the deck
            dealing_config (dict, optional): Configuration for dealing cards

        Returns:
            GameRuleSet: The created rule set instance
        """
        # Check if a rule set with this name already exists
        existing = cls.nodes.filter(name=name)
        if existing and len(existing) > 0:
            raise ValueError(f"A rule set with name '{name}' already exists")

        version = f"action_cards-{uuid.uuid4().hex[:8]}"

        if deck_configuration is None:
            deck_configuration = {
                "card_types": ["standard"],
                "suits": ["hearts", "diamonds", "clubs", "spades"],
                "values": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            }

        if dealing_config is None:
            dealing_config = {
                "cards_per_player": 7,
                "min_cards": 1,
                "max_cards": 12
            }

        rule_parameters = {
            "deck_configuration": deck_configuration,
            "card_actions": card_actions,
            "targeting_rules": targeting_rules,
            "turn_flow": turn_flow,
            "win_conditions": win_conditions,
            "dealing_config": dealing_config
        }

        rule_set = cls(
            version=version,
            name=name,
            description=description,
            parameters=rule_parameters
        ).save()

        return rule_set

    @classmethod
    def create_idiot_card_game(cls, name, description, card_actions, targeting_rules,
                              turn_flow, win_conditions, play_rules, deck_configuration=None, dealing_config=None):
        """
        Create a rule set for the Idiot card game

        Args:
            name (str): Name of the rule set
            description (str): Description of the rule set
            card_actions (dict): Mapping of cards to their actions
            targeting_rules (dict): Rules for targeting players
            turn_flow (dict): Rules for turn progression
            win_conditions (list): Conditions that determine a winner
            play_rules (dict): Rules for card play and special conditions
            deck_configuration (dict, optional): Configuration for the deck
            dealing_config (dict, optional): Configuration for dealing cards

        Returns:
            GameRuleSet: The created rule set instance
        """
        # Check if a rule set with this name already exists
        existing = cls.nodes.filter(name=name)
        if existing and len(existing) > 0:
            raise ValueError(f"A rule set with name '{name}' already exists")

        version = f"idiot_cards-{uuid.uuid4().hex[:8]}"

        if deck_configuration is None:
            deck_configuration = {
                "card_types": ["standard"],
                "suits": ["hearts", "diamonds", "clubs", "spades"],
                "values": ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            }

        if dealing_config is None:
            dealing_config = {
                "cards_per_player": 4,
                "min_cards": 2,
                "max_cards": 8
            }

        rule_parameters = {
            "deck_configuration": deck_configuration,
            "card_actions": card_actions,
            "targeting_rules": targeting_rules,
            "turn_flow": turn_flow,
            "win_conditions": win_conditions,
            "play_rules": play_rules,
            "dealing_config": dealing_config
        }

        rule_set = cls(
            version=version,
            name=name,
            description=description,
            parameters=rule_parameters
        ).save()

        return rule_set
