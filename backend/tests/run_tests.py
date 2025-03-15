#!/usr/bin/env python
"""
Test runner for the backend tests
"""
import os
import sys
import django
from django.test.runner import DiscoverRunner

# Add the project root to the Python path
sys.path.insert(0, '/app')

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "card_game.settings")
django.setup()

# Run tests
test_runner = DiscoverRunner(verbosity=2)
failures = test_runner.run_tests(["backend.tests"])

if failures:
    sys.exit(1)
