from django.apps import AppConfig
import os
from neomodel import config

class CardGameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'card_game'

    def ready(self):
        """
        Override the ready method to configure neomodel when Django starts.
        This ensures the correct Neo4j URL is used regardless of what might be
        set elsewhere.
        """
        # Get the URL from environment or use a default that works with Docker Compose networking
        neo4j_url = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:password@neo4j:7687')

        # Force the configuration to use this URL
        config.DATABASE_URL = neo4j_url
        print(f"Configured neomodel to use: {config.DATABASE_URL}")
