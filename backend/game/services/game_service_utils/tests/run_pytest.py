#!/usr/bin/env python
"""
Pytest runner for the create_idiot_rule_set tests
"""
import os
import sys
import pytest

# Add the project root to the Python path
sys.path.insert(0, '/app')

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.card_game.settings")

# Run pytest
if __name__ == "__main__":
    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Run pytest on the tests directory
    sys.exit(pytest.main([current_dir]))
