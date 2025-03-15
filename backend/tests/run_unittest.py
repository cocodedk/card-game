#!/usr/bin/env python
"""
Script to run unit tests with the correct settings.
"""

import os
import sys
import unittest
import django

if __name__ == "__main__":
    # Set the Django settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.tests.test_settings'

    # Initialize Django
    django.setup()

    # Get the directory of this script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover(current_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with the appropriate code
    sys.exit(not result.wasSuccessful())
