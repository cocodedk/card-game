#!/usr/bin/env python
"""
Test runner for authentication tests.
This script sets up the correct Django settings and runs the tests.
"""

import os
import sys
import django
from django.test.runner import DiscoverRunner

if __name__ == "__main__":
    # Set the Django settings module
    os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.authentication.test_settings'

    # Initialize Django
    django.setup()

    # Create a test runner
    test_runner = DiscoverRunner(verbosity=2)

    # Run the tests
    failures = test_runner.run_tests(["backend.authentication.tests"])

    # Exit with the appropriate code
    sys.exit(bool(failures))
