#!/usr/bin/env python
"""
Standalone test runner for tests that don't require Neo4j
"""
import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, '/app')
# Add the backend directory to the Python path to find card_game module
sys.path.insert(0, '/app/backend')

# Get the directory of this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Only run standalone tests
loader = unittest.TestLoader()
suite = unittest.TestSuite()

# Add the standalone test
standalone_test = os.path.join(current_dir, "standalone_test.py")
if os.path.exists(standalone_test):
    standalone_suite = loader.discover(current_dir, pattern="standalone_test.py")
    suite.addTest(standalone_suite)

# Run the tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with non-zero code if tests failed
if not result.wasSuccessful():
    sys.exit(1)
