#!/usr/bin/env python
"""
Script to configure neomodel to use the correct Neo4j URL.
This script should be run before starting the Django application.
"""

import os
import sys
from neomodel import config

def configure_neo4j():
    """Configure neomodel to use the correct Neo4j URL"""
    # Get the URL from environment or use a default that works with Docker Compose networking
    neo4j_url = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:password@neo4j:7687')

    # Force the configuration to use this URL
    config.DATABASE_URL = neo4j_url
    print(f"Configured neomodel to use: {config.DATABASE_URL}")

if __name__ == "__main__":
    configure_neo4j()

    # If there are command-line arguments, execute them as a command
    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])
