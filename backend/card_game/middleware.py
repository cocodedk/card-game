import os
from neomodel import config

class Neo4jConfigMiddleware:
    """
    Middleware to ensure the correct Neo4j connection URL is used.
    This runs on every request to ensure the connection is always correct.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Set the Neo4j URL when the middleware is initialized
        self.configure_neo4j()

    def __call__(self, request):
        # Set the Neo4j URL on each request to ensure it's always correct
        self.configure_neo4j()

        # Process the request
        response = self.get_response(request)
        return response

    def configure_neo4j(self):
        """Configure neomodel to use the correct Neo4j URL"""
        # Get the URL from environment or use a default that works with Docker Compose networking
        neo4j_url = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:password@neo4j:7687')

        # Force the configuration to use this URL
        config.DATABASE_URL = neo4j_url
