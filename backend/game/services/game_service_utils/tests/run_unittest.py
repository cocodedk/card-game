#!/usr/bin/env python
"""
Unittest runner for the create_idiot_rule_set tests
"""
import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, '/app')

# Get the directory of this script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Discover and run tests
loader = unittest.TestLoader()
suite = loader.discover(current_dir, pattern="test_*.py")

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with non-zero code if tests failed
if not result.wasSuccessful():
    sys.exit(1)
