"""
Configuration file for pytest
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.insert(0, '/app')

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.card_game.settings")
django.setup()
