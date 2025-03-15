# Test package for game_service
import sys
import os
from unittest.mock import MagicMock

# Add the project root to the Python path
sys.path.insert(0, '/app')

# Mock Django and related modules to avoid Django initialization issues
sys.modules['django'] = MagicMock()
sys.modules['django.test'] = MagicMock()
sys.modules['django.test.TestCase'] = MagicMock()

# Mock the models module to avoid import errors
class MockGameBaseModel:
    """Mock base model class"""
    pass

class MockGameRuleSet:
    """Mock GameRuleSet class"""
    @classmethod
    def create_idiot_card_game(cls, **kwargs):
        mock_rule_set = MagicMock()
        mock_rule_set.name = kwargs.get('name')
        mock_rule_set.description = kwargs.get('description')
        mock_rule_set.parameters = kwargs
        return mock_rule_set

# Create mock modules
sys.modules['game'] = MagicMock()
sys.modules['game.models'] = MagicMock()
sys.modules['game.models.base'] = MagicMock()
sys.modules['game.models.base'].GameBaseModel = MockGameBaseModel

sys.modules['backend.game.models'] = MagicMock()
sys.modules['backend.game.models'].GameRuleSet = MockGameRuleSet

# Import the function to test directly from the file
import importlib.util
spec = importlib.util.spec_from_file_location(
    "create_idiot_rule_set",
    "/app/backend/game/services/game_service/create_idiot_rule_set.py"
)
create_idiot_rule_set_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(create_idiot_rule_set_module)
create_idiot_rule_set = create_idiot_rule_set_module.create_idiot_rule_set

__all__ = ["create_idiot_rule_set"]
