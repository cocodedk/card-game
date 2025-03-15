from .action_card_rule_interpreter import ActionCardRuleInterpreter

def get_rule_interpreter(rule_set):
    """
    Factory function to get the appropriate rule interpreter

    Args:
        rule_set (GameRuleSet): The rule set to interpret

    Returns:
        GameRuleInterpreter: An appropriate interpreter instance
    """
    game_type = rule_set.version.split('-')[0]

    if game_type == "action_cards":
        return ActionCardRuleInterpreter(rule_set)
    elif game_type == "idiot_cards":
        return ActionCardRuleInterpreter(rule_set)  # Uses the same interpreter with different extensions
    else:
        raise ValueError(f"No interpreter available for game type: {game_type}")
